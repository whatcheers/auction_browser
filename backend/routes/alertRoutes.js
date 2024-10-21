const express = require('express');
const router = express.Router();
const { getDbConnection } = require('../utils/db');

const tables = ['backes', 'bidspotter', 'govdeals', 'gsa', 'hibid', 'proxibid', 'publicsurplus', 'smc', 'wiscosurp_auctions'];

router.get('/alerts', async (req, res) => {
    try {
        const connection = await getDbConnection();
        const [results] = await connection.execute('SELECT * FROM alerts');
        await connection.end();
        res.json(results);
    } catch (error) {
        console.error('Error fetching alerts:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.get('/alerts/latest', async (req, res) => {
    try {
        const connection = await getDbConnection();
        const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
        const [results] = await connection.execute('SELECT * FROM alerts WHERE date_added > ?', [oneHourAgo]);
        await connection.end();
        res.json(results);
    } catch (error) {
        console.error('Error fetching latest alerts:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.post('/alerts/search', async (req, res) => {
    const { item_name } = req.body;

    if (!item_name) {
        return res.status(400).json({ message: 'Invalid alert data' });
    }

    try {
        const connection = await getDbConnection();
        let searchResults = [];

        for (const table of tables) {
            const [results] = await connection.execute(`SELECT * FROM ${table} WHERE item_name LIKE ?`, [`%${item_name}%`]);
            searchResults = searchResults.concat(results);
        }

        await connection.end();
        res.json(searchResults);
    } catch (error) {
        console.error('Error searching alerts:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.post('/alerts', async (req, res) => {
    const { item } = req.body;

    if (!item || !item.name) {
        return res.status(400).json({ message: 'Invalid alert data' });
    }

    try {
        const connection = await getDbConnection();
        const [result] = await connection.execute(
            'INSERT INTO alerts (item_name, keyword) VALUES (?, ?)',
            [item.name, item.name] // Using item_name as keyword
        );
        await connection.end();

        res.status(201).json({ id: result.insertId, item_name: item.name, keyword: item.name });
    } catch (error) {
        console.error('Error adding alert:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.get('/alerts/new', async (req, res) => {
    try {
        const { startDate, endDate } = req.query;
        if (!startDate || !endDate) {
            return res.status(400).json({ message: 'Start date and end date are required' });
        }

        const connection = await getDbConnection();
        const [results] = await connection.execute(`
            SELECT a.id, a.item_name, i.url, i.time_left, i.latitude, i.longitude, i.location, 
                   i.lot_number, i.table_name
            FROM alerts a
            JOIN (
                ${tables.map(t => `
                    SELECT item_name, url, time_left, latitude, longitude, location, 
                           lot_number, '${t}' AS table_name
                    FROM ${t}
                    WHERE time_left > NOW() AND DATE(time_left) BETWEEN ? AND ?
                `).join(' UNION ALL ')}
            ) i ON i.item_name LIKE CONCAT('%', a.item_name, '%')
            WHERE i.time_left > NOW() AND DATE(i.time_left) BETWEEN ? AND ?
            ORDER BY i.time_left ASC
        `, [...Array(tables.length * 2).fill(startDate, endDate).flat(), startDate, endDate]);
        await connection.end();
        
        if (results.length === 0) {
            return res.status(404).json({ message: 'No data found for the specified date range' });
        }
        
        res.json(results);
    } catch (error) {
        console.error('Error fetching new alerts:', error);
        res.status(500).json({ message: 'Internal server error', error: error.message });
    }
});

router.get('/alerts/test', (req, res) => {
    res.json({ message: 'Alert routes are working' });
});

// Add this new route to delete an alert
router.delete('/alerts/:id', async (req, res) => {
    const { id } = req.params;
    try {
        const connection = await getDbConnection();
        const [result] = await connection.execute('DELETE FROM alerts WHERE id = ?', [id]);
        await connection.end();
        
        if (result.affectedRows > 0) {
            res.json({ success: true, message: 'Alert dismissed successfully' });
        } else {
            res.status(404).json({ success: false, message: 'Alert not found' });
        }
    } catch (error) {
        console.error('Error dismissing alert:', error);
        res.status(500).json({ success: false, message: 'Internal server error' });
    }
});

module.exports = router;
