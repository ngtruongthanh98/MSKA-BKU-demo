const fs = require('fs');
const path = require('path');

exports.getVideo = (req, res) => {
  const { videoName } = req.body;
  console.log(`Received videoName: ${videoName}`);

  const filePath = path.resolve(__dirname, '../../data/results.json');

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading file:', err);
      return res.status(500).send('Error reading file');
    }

    try {
      const results = JSON.parse(data);
      const result = results.find(entry => entry.name.includes(videoName));

      if (result) {
        const videoUrl = `https://storage.googleapis.com/bkuphoenix14t/${videoName}`;
        res.send({ videoUrl });
      } else {
        res.status(404).send('Video name not found');
      }
    } catch (parseError) {
      console.error('Error parsing JSON:', parseError);
      res.status(500).send('Error parsing JSON');
    }
  });
};
