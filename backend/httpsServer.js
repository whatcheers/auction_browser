require('dotenv').config();
const fs = require('fs');
const https = require('https');
const app = require('./server');
const cors = require('cors');

const privateKey = fs.readFileSync(process.env.SSL_KEY_PATH, 'utf8');
const certificate = fs.readFileSync(process.env.SSL_CERT_PATH, 'utf8');

app.use(cors({
  origin: process.env.CORS_ORIGIN,
  credentials: true
}));

const httpsOptions = {
  key: privateKey,
  cert: certificate,
};

const port = process.env.PORT || 3002;
const server = https.createServer(httpsOptions, app);

server.listen(port, (err) => {
  if (err) {
    console.error('Failed to start HTTPS server:', err);
    process.exit(1);
  }
  console.log(`HTTPS Server running on port ${port}`);
});

module.exports = server;