const fs = require('fs');
const path = require('path');

const manifestPath = path.resolve(__dirname, '../../data/demo_manifest.json');

function loadManifest() {
  const data = fs.readFileSync(manifestPath, 'utf8');
  return JSON.parse(data);
}

exports.listDemoVideos = (req, res) => {
  try {
    const manifest = loadManifest();
    const summaries = manifest.map(({ name, category, gtncFlag }) => ({ name, category, gtncFlag }));
    res.json(summaries);
  } catch (err) {
    console.error('Error reading demo manifest:', err);
    res.status(500).send('Error reading demo manifest');
  }
};

exports.getDemoResult = (req, res) => {
  const { videoName } = req.body;

  if (!videoName) {
    return res.status(400).send('videoName is required');
  }

  try {
    const manifest = loadManifest();
    const result = manifest.find((entry) => entry.name === videoName);

    if (!result) {
      return res.status(404).send('Video name not found in demo manifest');
    }

    res.json(result);
  } catch (err) {
    console.error('Error reading demo manifest:', err);
    res.status(500).send('Error reading demo manifest');
  }
};
