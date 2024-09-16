const express = require('express');
const router = express.Router();
const { getAuctionData, getDailyAveragesData, searchAuctionData } = require('../controllers/auctionController');

if (typeof getAuctionData !== 'function') {
    throw new Error('getAuctionData function is not defined properly');
}

router.get('/get-auction-data', getAuctionData);
router.get('/api/daily-averages', getDailyAveragesData);
router.get('/search-auction-data', searchAuctionData); // Add this line

module.exports = router;