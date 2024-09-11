const express = require('express');
const router = express.Router();
const { getDailyAveragesData } = require('../controllers/dailyAveragesController');

router.get('/daily-averages', getDailyAveragesData);

module.exports = router;