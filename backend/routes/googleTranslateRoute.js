const express = require('express');
const router = express.Router();
const translateController = require('../controllers/googleTranslateController');

router.post('/', translateController.translateText);

module.exports = router;
