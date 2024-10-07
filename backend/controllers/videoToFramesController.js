const fs = require('fs');
const path = require('path');
const axios = require('axios');

exports.getVideoFrames = (req, res) => {
  const { videoName } = req.body;
  console.log(`Received videoName: ${videoName}`);

  const filePath = path.resolve(__dirname, '../../data/results.json');

  fs.readFile(filePath, 'utf8', async (err, data) => {
    if (err) {
      console.error('Error reading file:', err);
      return res.status(500).send('Error reading file');
    }

    try {
      const results = JSON.parse(data);
      const result = results.find(entry => entry.name.includes(videoName));

      if (result) {
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

        res.send({ imageArray });
      } else {
        res.status(404).send('Video name not found');
      }
    } catch (parseError) {
      console.error('Error parsing JSON:', parseError);
      res.status(500).send('Error parsing JSON');
    }
  });
};
