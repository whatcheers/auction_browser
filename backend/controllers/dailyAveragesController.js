const { getDbConnection } = require('../utils/db');
const { logError } = require('../utils/logger');

async function getDailyAveragesData(req, res) {
  try {
    const connection = await getDbConnection();
    console.log('Database connection established');
    const query = `
      SELECT 
        DATE(timestamp) as date,
        AVG(auctions_scraped) as avg_auctions_scraped,
        AVG(items_added) as avg_items_added,
        AVG(items_updated) as avg_items_updated,
        AVG(items_removed) as avg_items_removed,
        AVG(items_skipped) as avg_items_skipped,
        AVG(errors) as avg_errors,
        AVG(addresses_processed) as avg_addresses_processed,
        AVG(addresses_updated) as avg_addresses_updated,
        AVG(addresses_skipped) as avg_addresses_skipped
      FROM statistics
      GROUP BY DATE(timestamp)
    `;
    const [rows] = await connection.execute(query);
    res.json(rows);
  } catch (error) {
    console.error('Detailed error:', error);
    await logError('Error fetching daily averages data', error);
    console.error('Error fetching daily averages data:', error);
    res.status(500).json({ error: 'Failed to fetch daily averages data', details: error.message });
  }
}

module.exports = { getDailyAveragesData };