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
        const tables = ['backes', 'bidspotter', 'govdeals', 'gsa', 'hibid', 'proxibid', 'publicsurplus', 'smc', 'wiscosurp_auctions'];
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
    const { keyword, item } = req.body;

    if (!keyword || !item || !item.name) {
        return res.status(400).json({ message: 'Invalid alert data' });
    }

    try {
        const connection = await getDbConnection();
        const [result] = await connection.execute(
            'INSERT INTO alerts (item_name, keyword) VALUES (?, ?)',
            [item.name, keyword]
        );
        await connection.end();

        res.status(201).json({ id: result.insertId, item_name: item.name, keyword });
    } catch (error) {
        console.error('Error adding alert:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.get('/alerts/new', async (req, res) => {
    try {
        const connection = await getDbConnection();
        const lastCheckTime = req.query.lastCheck || new Date(0).toISOString();
        const [results] = await connection.execute(`
            SELECT a.keyword, i.item_name, i.url, i.date_added
            FROM alerts a
            JOIN (
                SELECT item_name, url, date_added
                FROM (${tables.map(t => `SELECT item_name, url, date_added FROM ${t}`).join(' UNION ALL ')})
                AS all_items
                WHERE date_added > ?
            ) i ON i.item_name LIKE CONCAT('%', a.keyword, '%')
            ORDER BY i.date_added DESC
        `, [lastCheckTime]);
        await connection.end();
        res.json(results);
    } catch (error) {
        console.error('Error fetching new alerts:', error);
        res.status(500).json({ message: 'Internal server error' });
    }
});

router.get('/alerts/test', (req, res) => {
    res.json({ message: 'Alert routes are working' });
});

module.exports = router;
