const express = require('express');
const router = express.Router();
const { getAuctionData } = require('../controllers/auctionController');

// Define auction routes
router.get('/get-auction-data', getAuctionData);

module.exports = router;