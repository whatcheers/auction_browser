// utils/logger.js
const fs = require('fs').promises;
const path = require('path');

const logFile = path.join(__dirname, '..', 'server.log');

const logError = async (message, error) => {
  console.error(`[ERROR] ${new Date().toISOString()} - ${message}`, error);
  // Any additional error logging logic
};

const logInfo = (message) => {
  console.log(`[INFO] ${new Date().toISOString()} - ${message}`);
};

module.exports = { logError, logInfo };