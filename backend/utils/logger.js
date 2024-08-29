// utils/logger.js
const fs = require('fs').promises;
const path = require('path');

const logFile = path.join(__dirname, '..', 'server.log');

async function logError(message, error) {
  const errorLog = `${new Date().toISOString()} - ERROR: ${message}\n${error.stack}\n`;
  console.error(errorLog);
  await fs.appendFile(logFile, errorLog);
}

module.exports = { logError };