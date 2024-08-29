const { getDbConnection } = require('../utils/db');
const { logError } = require('../utils/logger');
const axios = require('axios');

const tableNames = {
  backes: 'backes',
  bidspotter: 'bidspotter',
  govdeals: 'govdeals',
  gsa: 'gsa',
  hibid: 'hibid',
  publicsurplus: 'publicsurplus',
  proxibid: 'proxibid',
  smc: 'smc',
  wiscosurp_auctions: 'wiscosurp_auctions',
};

async function getAuctionData(req, res) {
  let { tableName, startDate, endDate } = req.query;

  if (!tableName) {
    return res.status(400).json({ error: 'TableName parameter is required' });
  }

  if (tableName === 'ending_today') {
    const currentDate = new Date().toISOString().split('T')[0];
    startDate = currentDate;
    endDate = currentDate;
  } else if (!startDate || !endDate) {
    return res.status(400).json({ error: 'StartDate and EndDate parameters are required' });
  }

  let connection;
  try {
    connection = await getDbConnection();
    let data = [];

    if (tableName === 'all_tables') {
      for (const [key, table] of Object.entries(tableNames)) {
        const query = `
          SELECT *, '${key}' as table_name 
          FROM ${table}
          WHERE DATE(time_left) BETWEEN ? AND ?
        `;
        const [rows] = await connection.execute(query, [startDate, endDate]);
        data = data.concat(rows);
      }
    } else if (tableName === 'ending_today') {
      const todayResponse = await axios.get('https://hashbrowns/bin/get_auction_data.php?todayOnly=true');
      data = todayResponse.data;
    } else if (tableName in tableNames) {
      const query = `
        SELECT * FROM ${tableNames[tableName]}
        WHERE DATE(time_left) BETWEEN ? AND ?
      `;
      const [rows] = await connection.execute(query, [startDate, endDate]);
      data = rows;
    } else {
      return res.status(400).json({ error: `Invalid table name: ${tableName}` });
    }

    if (data.length === 0) {
      return res.status(404).json({ error: 'No data found for the specified date range' });
    }

    res.json(data);
  } catch (error) {
    await logError('Error fetching auction data', error);
    console.error('Error fetching auction data:', error);
    res.status(500).json({ error: 'Failed to fetch auction data', details: error.message });
  } finally {
    if (connection) {
      await connection.end();
    }
  }
}

module.exports = { getAuctionData };