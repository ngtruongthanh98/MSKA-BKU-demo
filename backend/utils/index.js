const axios = require('axios');
const path = require('path');
const fs = require('fs');
const ffmpeg = require('fluent-ffmpeg');

const convertVideoToFrames = (videoPath, videoName) => {
  return new Promise((resolve, reject) => {
    const outputDir = path.join(__dirname, '..', 'frames', videoName);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    ffmpeg(videoPath)
      .on('end', () => {
        const imageArray = fs.readdirSync(outputDir).map((file) => path.join(outputDir, file));
        resolve(imageArray);
      })
      .on('error', (err) => {
        reject(err);
      })
      .save(`${outputDir}/frame%04d.png`);
  });
};

async function videoToFramesInternal(videoName) {
  const baseUrl = 'https://storage.googleapis.com/phoenix14tframebku/';
  const imageArray = [];

  for (let i = 1; ; i++) {
    let url = `${baseUrl}${videoName}/images${String(i).padStart(4, '0')}.png`;

    try {
      await axios.head(url);
      imageArray.push(url);
    } catch (error) {
      break;
    }
  }

  return imageArray;
}

module.exports = { videoToFramesInternal, convertVideoToFrames };
