const multer = require('multer');
const path = require('path');
const fs = require('fs');

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
  res.send({ filePath: req.file.path });
};

module.exports = {
  upload,
  uploadVideo,
};
