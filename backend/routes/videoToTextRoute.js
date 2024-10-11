const express = require('express');
const { upload, uploadVideo } = require('../controllers/videoToTextController');

const router = express.Router();

router.post('/video-to-text', upload.single('file'), uploadVideo);

module.exports = router;
