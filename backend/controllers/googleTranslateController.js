const { translate } = require('@vitalets/google-translate-api');

exports.translateText = async (req, res) => {
  const { text, target } = req.body;

  if (!text || !target) {
    return res.status(400).send('Missing required fields: text, target');
  }

  try {
    const { text: translatedText } = await translate(text, { to: target });
    res.json({ translatedText });
  } catch (error) {
    console.error('Error translating text:', error);
    res.status(500).send('Error translating text');
  }
};
