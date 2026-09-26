const express = require('express');
const { listDemoVideos, getDemoResult } = require('../controllers/demoController');

const router = express.Router();

router.get('/videos', listDemoVideos);
router.post('/translate', getDemoResult);

module.exports = router;
