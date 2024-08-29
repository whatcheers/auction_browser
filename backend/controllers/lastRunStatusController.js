// controllers/lastRunStatusController.js
const fs = require('fs').promises;
const path = require('path');
const { logError } = require('../utils/logger');

async function getLastRunStatus(req, res) {
  try {
    const filePath = path.join(__dirname, '..', 'last_run_status.json');
    const data = await fs.readFile(filePath, 'utf8');
    res.json(JSON.parse(data));
  } catch (error) {
    await logError('Failed to read last run status', error);
    res.status(500).json({ error: 'Failed to read last run status' });
  }
}

module.exports = { getLastRunStatus };