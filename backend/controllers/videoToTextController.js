const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { convertVideoToFrames } = require('../utils');
const axios = require('axios');

// Multer setup for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, `${file.originalname}`);
  },
});
const upload = multer({ storage: storage });

// Create uploads directory if it doesn't exist
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

// Controller function to handle file upload
const uploadVideo = (req, res) => {
  console.log('File uploaded:', req.file);

  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  const videoPath = req.file.path;
  const videoName = path.basename(videoPath, path.extname(videoPath));

  convertVideoToFrames(videoPath, videoName)
    .then((imageArray) => {
      // res.send({ filePath: req.file.path, frames: imageArray });

      //TODO: handle send frames to Flask server

      try {
        axios.post('http://localhost:5000/translate-sign-video', { videoName, imageArray })
          .then(response => {
            console.log('Response:', response.data);
            res.send(response.data);
          })
          .catch(error => {
            console.error('Error calling API:', error);
            res.status(500).send('Error calling API');
          });
      } catch (parseError) {
        console.error('Error parsing JSON:', parseError);
        res.status(500).send('Error parsing JSON');
      }
    })
    .catch((error) => {
      console.error('Error converting video to frames:', error);
      res.status(500).send('Error converting video to frames.');
    });
};

module.exports = {
  upload,
  uploadVideo,
};
