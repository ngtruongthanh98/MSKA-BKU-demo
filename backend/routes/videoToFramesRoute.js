const express = require('express');
const router = express.Router();
const getVideoFramesController = require('../controllers/videoToFramesController');

router.post('/', getVideoFramesController.getVideoFrames);

module.exports = router;
