const axios = require('axios');

async function videoToFrames(videoName) {
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

module.exports = { videoToFrames };
