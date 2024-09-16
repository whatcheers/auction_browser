const { getDbConnection } = require('../utils/db');
const { logError, logInfo } = require('../utils/logger');
const axios = require('axios');
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 300, checkperiod: 320 });

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
  let { tableName, startDate, endDate, searchTerm } = req.query;

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

  const cacheKey = `auction_data_${tableName}_${startDate}_${endDate}_${searchTerm || ''}`;
  logInfo(`Checking cache for key: ${cacheKey}`);
  const cachedData = cache.get(cacheKey);
  if (cachedData) {
    logInfo(`Cache hit for key: ${cacheKey}`);
    return res.json(cachedData);
  }
  logInfo(`Cache miss for key: ${cacheKey}`);

  let connection;
  try {
    connection = await getDbConnection();
    let data = [];

    const searchCondition = searchTerm ? `AND item_name LIKE ?` : '';
    const searchParams = searchTerm ? [`%${searchTerm}%`] : [];

    if (tableName === 'all_tables') {
      for (const [key, table] of Object.entries(tableNames)) {
        const query = `
          SELECT *, '${key}' as table_name 
          FROM ${table}
          WHERE DATE(time_left) BETWEEN ? AND ? 
          ${searchTerm ? `AND item_name LIKE ?` : ''}
        `;
        const params = [startDate, endDate, ...searchParams];
        const [rows] = await connection.execute(query, params);
        data = data.concat(rows);
      }
    } else if (tableName === 'ending_today') {
      const todayResponse = await axios.get('https://hashbrowns/bin/get_auction_data.php?todayOnly=true');
      data = todayResponse.data;
    } else if (tableName in tableNames) {
      const query = `
        SELECT * FROM ${tableNames[tableName]}
        WHERE DATE(time_left) BETWEEN ? AND ? 
        ${searchTerm ? `AND item_name LIKE ?` : ''}
      `;
      const params = [startDate, endDate, ...searchParams];
      const [rows] = await connection.execute(query, params);
      data = rows;
    } else {
      return res.status(400).json({ error: `Invalid table name: ${tableName}` });
    }

    if (data.length === 0) {
      logInfo(`No data found for ${tableName} between ${startDate} and ${endDate}`);
      return res.status(404).json({ error: 'No data found for the specified date range' });
    }

    logInfo(`Caching data for key: ${cacheKey}`);
    cache.set(cacheKey, data);
    logInfo(`Data cached successfully for key: ${cacheKey}`);
    res.json(data);
  } catch (error) {
    await logError('Error fetching auction data', error);
    console.error('Error fetching auction data:', error);
    res.status(500).json({ error: 'Failed to fetch auction data', details: error.message });
  } finally {
    if (connection) await connection.end();
  }
}

async function getDailyAveragesData(req, res) {
    try {
        // Your logic to fetch and return daily averages data
    } catch (error) {
        await logError('Error fetching daily averages data', error);
        console.error('Error fetching daily averages data:', error);
        res.status(500).json({ error: 'Failed to fetch daily averages data', details: error.message });
    }
}

async function searchAuctionData(req, res) {
  let { tableName, startDate, endDate, searchTerm } = req.query;

  if (!tableName || !startDate || !endDate || !searchTerm) {
    return res.status(400).json({ error: 'TableName, StartDate, EndDate, and SearchTerm parameters are required' });
  }

  const cacheKey = `search_auction_data_${tableName}_${startDate}_${endDate}_${searchTerm}`;
  logInfo(`Checking cache for key: ${cacheKey}`);
  const cachedData = cache.get(cacheKey);
  if (cachedData) {
    logInfo(`Cache hit for key: ${cacheKey}`);
    return res.json(cachedData);
  }
  logInfo(`Cache miss for key: ${cacheKey}`);

  let connection;
  try {
    connection = await getDbConnection();
    let data = [];

    const searchCondition = `AND item_name LIKE ?`;
    const searchParams = [`%${searchTerm}%`];

    if (tableName === 'all_tables') {
      for (const [key, table] of Object.entries(tableNames)) {
        const query = `
          SELECT *, '${key}' as table_name 
          FROM ${table}
          WHERE DATE(time_left) BETWEEN ? AND ? 
          AND item_name LIKE ?
        `;
        const params = [startDate, endDate, `%${searchTerm}%`];
        const [rows] = await connection.execute(query, params);
        data = data.concat(rows);
      }
    } else if (tableName in tableNames) {
      const query = `
        SELECT * FROM ${tableNames[tableName]}
        WHERE DATE(time_left) BETWEEN ? AND ? 
        AND item_name LIKE ?
      `;
      const params = [startDate, endDate, `%${searchTerm}%`];
      const [rows] = await connection.execute(query, params);
      data = rows;
    } else {
      return res.status(400).json({ error: `Invalid table name: ${tableName}` });
    }

    if (data.length === 0) {
      logInfo(`No data found for ${tableName} between ${startDate} and ${endDate} with search term "${searchTerm}"`);
      return res.status(404).json({ error: 'No data found for the specified search criteria' });
    }

    logInfo(`Caching data for key: ${cacheKey}`);
    cache.set(cacheKey, data);
    logInfo(`Data cached successfully for key: ${cacheKey}`);
    res.json(data);
  } catch (error) {
    await logError('Error searching auction data', error);
    console.error('Error searching auction data:', error);
    res.status(500).json({ error: 'Failed to search auction data', details: error.message });
  } finally {
    if (connection) await connection.end();
  }
}

module.exports = { getAuctionData, getDailyAveragesData, searchAuctionData };