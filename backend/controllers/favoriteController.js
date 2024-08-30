const { getDbConnection } = require('../utils/db');
const { logError } = require('../utils/logger');
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

async function updateFavorite(req, res) {
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
      cache.del('favorites'); // Clear the favorites cache
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
}

async function getFavorites(req, res) {
  const cacheKey = 'favorites';
  const cachedFavorites = cache.get(cacheKey);
  if (cachedFavorites) {
    return res.json(cachedFavorites);
  }

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

    cache.set(cacheKey, processedFavorites);
    res.json(processedFavorites);
  } catch (error) {
    await logError('Error fetching favorites', error);
    res.status(500).json({ error: 'Failed to fetch favorites', details: error.message });
  } finally {
    if (connection) await connection.end();
  }
}

module.exports = { updateFavorite, getFavorites };