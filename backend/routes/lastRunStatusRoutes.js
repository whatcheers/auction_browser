// routes/lastRunStatusRoutes.js
const express = require('express');
const { getLastRunStatus } = require('../controllers/lastRunStatusController');
const router = express.Router();

router.get('/last-run-status', getLastRunStatus);

module.exports = router;