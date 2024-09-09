const express = require('express');
const router = express.Router();
const { getAuctionData, searchAuctionData } = require('../controllers/auctionController');

// Define auction routes
router.get('/get-auction-data', getAuctionData);
router.get('/search-auction-data', searchAuctionData);

module.exports = router;