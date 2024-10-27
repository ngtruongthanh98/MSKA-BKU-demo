const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());

const videoToTextRoute = require('./routes/videoToTextRoute');
app.use('/api', videoToTextRoute);

const translateRoute = require('./routes/signLanguageTranslateRoute');
app.use('/api/sl-translate', translateRoute);

const googleTranslateRoute = require('./routes/googleTranslateRoute');
app.use('/api/google-translate', googleTranslateRoute);

const getVideoRoute = require('./routes/getVideoRoute');
app.use('/api/get-video', getVideoRoute);

const videoToFramesRoute = require('./routes/videoToFramesRoute');
app.use('/api/video-to-frames', videoToFramesRoute);

const flaskServerUrl = `${process.env.MSKA_SERVER_PATH}receive-images`;

app.post('/api/send-images', async (req, res) => {
  const { imageArray, videoName } = req.body;

  try {
    await axios.post(flaskServerUrl, { imageArray, videoName });
    res.send('Images sent to Flask server');
  } catch (error) {
    console.error('Error sending images to Flask server:', error);
    res.status(500).send('Error sending images to Flask server');
  }
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
