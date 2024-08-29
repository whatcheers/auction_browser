const express = require('express');
const { updateFavorite, getFavorites } = require('../controllers/favoriteController');
const router = express.Router();

// Define favorite routes
router.post('/favorite', updateFavorite);
router.get('/favorites', getFavorites);

module.exports = router;