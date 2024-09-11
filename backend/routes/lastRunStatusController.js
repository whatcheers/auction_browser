const { getDbConnection } = require('../utils/db');
const { logError } = require('../utils/logger');

async function getLastRunStatus(req, res) {
    try {
        const connection = await getDbConnection();
        const query = `
            SELECT timestamp 
            FROM statistics 
            ORDER BY timestamp DESC 
            LIMIT 1
        `;
        const [rows] = await connection.execute(query);
        if (rows.length > 0) {
            res.json({ lastRun: rows[0].timestamp });
        } else {
            res.status(404).json({ error: 'No run status found' });
        }
    } catch (error) {
        await logError('Error fetching last run status', error);
        console.error('Error fetching last run status:', error);
        res.status(500).json({ error: 'Failed to fetch last run status', details: error.message });
    }
}

module.exports = { getLastRunStatus };
