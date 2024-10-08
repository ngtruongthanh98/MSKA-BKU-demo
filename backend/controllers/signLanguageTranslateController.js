const fs = require('fs');
const path = require('path');
const axios = require('axios');

exports.translateVideoToText = (req, res) => {
  const { videoName } = req.body;
  console.log(`Received videoName: ${videoName}`);

  if (!videoName) {
    return res.status(400).send('videoName is required');
  }

  const filePath = path.resolve(__dirname, '../../data/results.json');

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading file:', err);
      return res.status(500).send('Error reading file');
    }

    try {
      // call API to Flask Server port 5000, send videoName and get response
      axios.post('http://localhost:5000/translate', { videoName })
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
  });
};
