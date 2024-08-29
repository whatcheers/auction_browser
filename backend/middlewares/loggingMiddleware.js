const fs = require('fs').promises;
const path = require('path');
const logFile = path.join(__dirname, '..', 'server.log');

async function loggingMiddleware(req, res, next) {
  const logMessage = `${new Date().toISOString()} - ${req.method} ${req.url}\n`;
  await fs.appendFile(logFile, logMessage);
  console.log(logMessage.trim());
  next();
}

module.exports = loggingMiddleware;
