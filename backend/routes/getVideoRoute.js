const express = require('express');
const router = express.Router();
const getVideoController = require('../controllers/getVideoController');

router.post('/', getVideoController.getVideo);

module.exports = router;
