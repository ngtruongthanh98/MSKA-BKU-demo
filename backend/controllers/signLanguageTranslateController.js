const fs = require('fs');
const path = require('path');

exports.translateImage = (req, res) => {
  const { imageName } = req.body;
  console.log(`Received imageName: ${imageName}`);

  const filePath = path.resolve(__dirname, '../../data/results.json');

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading file:', err);
      return res.status(500).send('Error reading file');
    }

    try {
      const results = JSON.parse(data);
      const result = results.find(entry => entry.name.includes(imageName));

      if (result) {
        res.send(result.txt_hyp);
      } else {
        res.status(404).send('Image name not found');
      }
    } catch (parseError) {
      console.error('Error parsing JSON:', parseError);
      res.status(500).send('Error parsing JSON');
    }
  });
};
