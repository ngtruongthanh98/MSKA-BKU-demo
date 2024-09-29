const express = require('express');
const router = express.Router();
const translateController = require('../controllers/signLanguageTranslateController');

router.post('/', translateController.translateImage);

module.exports = router;
