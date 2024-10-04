require('dotenv').config();
const express = require('express');
const cors = require('cors');
const loggingMiddleware = require('./middlewares/loggingMiddleware');
const auctionRoutes = require('./routes/auctionRoutes');
const favoriteRoutes = require('./routes/favoriteRoutes');
const dailyAveragesRoutes = require('./routes/dailyAveragesRoutes');
const alertRoutes = require('./routes/alertRoutes');
const app = express();

app.use(cors({
  origin: process.env.CORS_ORIGIN,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json({ limit: '200mb' }));
app.use(loggingMiddleware);
app.use(loggingMiddleware);

app.use('/api', auctionRoutes);
app.use('/api', favoriteRoutes);
app.use('/api', dailyAveragesRoutes);
app.use('/api', alertRoutes);

module.exports = app;