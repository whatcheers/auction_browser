/**
 * Auction Data Server
 * 
 * This Express server provides endpoints for managing auction data,
 * including fetching auction items, managing favorites, and categorizing items.
 * It interacts with a MySQL database and external PHP endpoints.
 */

// Required dependencies
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const mysql = require('mysql2/promise');
const axios = require('axios');

// Import custom utility functions and configurations
const { endpoints, getCategoryFromUrl } = require('/var/www/html/auction-scraper/src/components/utils');
const { categorizeItems } = require('/var/www/html/auction-scraper/src/components/categorizeItems');

// Define the correct table names directly
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

// Initialize Express app and set port
const app = express();
const port = 3002;

// Database configuration
const dbConfig = {
  host: 'localhost',
  user: 'whatcheer',
  password: 'meatwad',
  database: 'auctions',
};

// CORS configuration
app.use(cors({
  origin: 'http://hashbrowns:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.options('*', cors());

// Parse JSON request bodies
app.use(express.json({ limit: '200mb' }));

// Path for the log file
const logFile = path.join(__dirname, 'server.log');

// Logging middleware
app.use(async (req, res, next) => {
  const logMessage = `${new Date().toISOString()} - ${req.method} ${req.url}\n`;
  await fs.appendFile(logFile, logMessage);
  console.log(logMessage.trim());
  next();
});

/**
 * Create a new database connection
 * @returns {Promise<mysql.Connection>} A promise that resolves to a database connection
 */
async function getDbConnection() {
  try {
    return await mysql.createConnection(dbConfig);
  } catch (error) {
    console.error('Error creating database connection:', error);
    throw new Error('Failed to connect to the database');
  }
}

/**
 * Log errors to both console and file
 * @param {string} message - Error message
 * @param {Error} error - Error object
 */
async function logError(message, error) {
  const errorLog = `${new Date().toISOString()} - ERROR: ${message}\n${error.stack}\n`;
  console.error(errorLog);
  await fs.appendFile(logFile, errorLog);
}

/**
 * Route to get the last run status
 */
app.get('/bin/last-run-status', async (req, res) => {
  try {
    const filePath = path.join(__dirname, 'last_run_status.json');
    const data = await fs.readFile(filePath, 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    await logError('Failed to read last run status', error);
    res.status(500).json({ error: 'Failed to read last run status' });
  }
});

/**
 * Route to categorize items
 */
app.post('/api/categorize-items', (req, res) => {
  try {
    const categorizedResults = categorizeItems(req.body);
    res.json(categorizedResults);
  } catch (error) {
    logError('Error categorizing items', error);
    res.status(500).json({ error: 'Failed to categorize items' });
  }
});
/**
 * Route to fetch auction data from all tables
 */
app.get('/api/get-auction-data', async (req, res) => {
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

  let connection;  // Declare connection here

  try {
    connection = await getDbConnection();
    let data = [];

    if (tableName === 'all_tables') {
      // Query all tables if "all_tables" is specified
      for (const [key, table] of Object.entries(tableNames)) {
        const query = `
          SELECT *, '${key}' as table_name 
          FROM ${table}
          WHERE DATE(time_left) BETWEEN ? AND ?
        `;
        const [rows] = await connection.execute(query, [startDate, endDate]);
        data = data.concat(rows);
      }
    } else if (tableName in tableNames) {
      // Query a specific table if a valid table name is provided
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
    res.status(500).json({ error: 'Failed to fetch auction data' });
  } finally {
    if (connection) {  // Ensure connection is defined before ending it
      await connection.end();
    }
  }
});


/**
 * Route to update favorite status
 */
app.post('/api/favorite', async (req, res) => {
  const { favorite, tableName, lot_number, url, id } = req.body;

  if (!tableName || !url) {
    return res.status(400).json({ success: false, error: "Missing required data: tableName or url" });
  }

  const identifierColumn = ['govdeals', 'gsa', 'bidspotter', 'backes', 'smc', 'wiscosurp_auctions', 'hibid', 'publicsurplus'].includes(tableName) ? 'lot_number' : 'id';
  const identifierValue = tableName === 'publicsurplus' ? parseInt(lot_number, 10) : (lot_number || id);

  const sql = `UPDATE ${tableName} SET favorite = ? WHERE url = ? AND ${identifierColumn} = ?`;
  const params = [favorite, url, identifierValue];

  let connection;
  try {
    connection = await getDbConnection();
    const [results] = await connection.execute(sql, params);
    if (results.affectedRows > 0) {
      res.json({ success: true });
    } else {
      res.json({ success: false, error: "No matching record found to update" });
    }
  } catch (error) {
    await logError('Database error in /api/favorite', error);
    res.status(500).json({ success: false, error: "Database error" });
  } finally {
    if (connection) await connection.end();
  }
});

/**
 * Route to search auction data
 */
app.get('/api/search-auction-data', async (req, res) => {
  const { tableName, searchTerm } = req.query;

  if (!tableName) {
    return res.status(400).json({ error: 'TableName parameter is required' });
  }

  if (!searchTerm) {
    return res.status(400).json({ error: 'SearchTerm parameter is required' });
  }

  let data = []; // To store results
  let connection;

  try {
    if (tableName === 'all_tables') {
      // Loop through all tables and aggregate results
      for (const [key, table] of Object.entries(tableNames)) {
        const query = `
          SELECT * FROM ${table}
          WHERE LOWER(item_name) LIKE ? 
          OR LOWER(location) LIKE ? 
          OR LOWER(lot_number) LIKE ?
        `;
        connection = await getDbConnection();
        const searchQuery = `%${searchTerm.toLowerCase()}%`;
        const [rows] = await connection.execute(query, [searchQuery, searchQuery, searchQuery]);
        data = data.concat(rows);  // Aggregate data from each table
      }
    } else {
      // Handle search within a specific table
      const table = tableNames[tableName]; // Validate the table name
      if (!table) {
        return res.status(400).json({ error: `Invalid table name: ${tableName}` });
      }

      const query = `
        SELECT * FROM ${table}
        WHERE LOWER(item_name) LIKE ? 
        OR LOWER(location) LIKE ? 
        OR LOWER(lot_number) LIKE ?
      `;
      connection = await getDbConnection();
      const searchQuery = `%${searchTerm.toLowerCase()}%`;
      const [rows] = await connection.execute(query, [searchQuery, searchQuery, searchQuery]);
      data = rows;  // Data for specific table
    }

    if (data.length === 0) {
      return res.status(404).json({ error: 'No data found for the specified search term' });
    }

    res.json(data);
  } catch (error) {
    await logError('Error searching auction data', error);
    res.status(500).json({ error: 'Failed to search auction data' });
  } finally {
    if (connection) await connection.end();
  }
});


/**
 * Route to fetch basic map data for all tables
 */
app.get('/api/get-map-data', async (req, res) => {
  const { startDate, endDate } = req.query;

  if (!startDate || !endDate) {
    return res.status(400).json({ error: 'StartDate and EndDate parameters are required' });
  }

  let mapData = [];
  let connection;

  try {
    connection = await getDbConnection();

    for (const [tableName, table] of Object.entries(tableNames)) {
      const query = `
        SELECT id, latitude, longitude, '${tableName}' as table_name 
        FROM ${table}
        WHERE DATE(time_left) BETWEEN ? AND ?
      `;

      const [rows] = await connection.execute(query, [startDate, endDate]);
      mapData = mapData.concat(rows);
    }

    // Handle 'ending_today' data
    const todayResponse = await axios.get('http://hashbrowns/bin/get_auction_data.php?todayOnly=true');
    if (todayResponse.data && Array.isArray(todayResponse.data)) {
      const todayMapData = todayResponse.data.map(item => ({
        id: item.id,
        latitude: item.latitude,
        longitude: item.longitude,
        table_name: 'ending_today'
      }));
      mapData = mapData.concat(todayMapData);
    }

    if (mapData.length === 0) {
      return res.status(404).json({ error: 'No data found for the specified date range' });
    }

    res.json(mapData);
  } catch (error) {
    await logError('Error fetching map data', error);
    res.status(500).json({ error: 'Failed to fetch map data' });
  } finally {
    if (connection) await connection.end();
  }
});

/**
 * Route to fetch detailed cluster data
 */
app.post('/api/get-cluster-data', async (req, res) => {
  const { ids, tableNames } = req.body;

  if (!ids || !tableNames || ids.length !== tableNames.length) {
    return res.status(400).json({ error: 'Invalid request body' });
  }

  let clusterData = [];
  let connection;

  try {
    connection = await getDbConnection();

    for (let i = 0; i < ids.length; i++) {
      const id = ids[i];
      const tableName = tableNames[i];

      if (tableName === 'ending_today') {
        const todayResponse = await axios.get(`http://hashbrowns/bin/get_auction_data.php?id=${id}`);
        if (todayResponse.data) {
          clusterData.push(todayResponse.data);
        }
      } else {
        const table = tableNames[tableName];
        if (!table) {
          console.warn(`Invalid table name: ${tableName}`);
          continue;
        }

        const query = `SELECT * FROM ${table} WHERE id = ?`;
        const [rows] = await connection.execute(query, [id]);
        if (rows.length > 0) {
          clusterData.push({ ...rows[0], table_name: tableName });
        }
      }
    }

    res.json(clusterData);
  } catch (error) {
    await logError('Error fetching cluster data', error);
    res.status(500).json({ error: 'Failed to fetch cluster data' });
  } finally {
    if (connection) await connection.end();
  }
});

/**
 * Route to fetch favorites
 */
app.get('/api/favorites', async (req, res) => {
  const tables = Object.values(tableNames);
  let allFavorites = [];

  let connection;
  try {
    connection = await getDbConnection();
    for (const table of tables) {
      try {
        const [rows] = await connection.query(
          `SELECT *, '${table}' as original_table FROM ${table} WHERE favorite = 'Y'`
        );
        allFavorites = allFavorites.concat(rows);
      } catch (tableError) {
        await logError(`Error fetching favorites from table ${table}`, tableError);
      }
    }

    const processedFavorites = allFavorites.map(item => ({
      ...item,
      current_bid: item.current_bid || 'N/A',
      favorite: 'Y',
      table_name: item.original_table,
    }));

    res.json(processedFavorites);
  } catch (error) {
    await logError('Error fetching favorites', error);
    res.status(500).json({ error: 'Failed to fetch favorites', details: error.message });
  } finally {
    if (connection) await connection.end();
  }
});

// Handle server shutdown
process.on('SIGINT', async () => {
  await fs.appendFile(logFile, 'Server shutting down\n');
  process.exit();
});

// Start the server
app.listen(port, async (err) => {
  if (err) {
    await logError('Error starting server', err);
    process.exit(1);
  }
  console.log(`Server running on port ${port}`);
  await fs.appendFile(logFile, `Server started on port ${port}\n`);
});

// Global error handler
process.on('uncaughtException', async (error) => {
  await logError('Uncaught Exception', error);
  process.exit(1);
});

process.on('unhandledRejection', async (reason, promise) => {
  await logError('Unhandled Rejection', new Error(`Unhandled Rejection at: ${promise}\nReason: ${reason}`));
  process.exit(1);
});