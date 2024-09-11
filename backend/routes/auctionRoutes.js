const express = require('express');
const router = express.Router();
const { getAuctionData, getDailyAveragesData } = require('../controllers/auctionController');

if (typeof getAuctionData !== 'function') {
    throw new Error('getAuctionData function is not defined properly');
}

router.get('/get-auction-data', getAuctionData);
router.get('/api/daily-averages', getDailyAveragesData);

module.exports = router;