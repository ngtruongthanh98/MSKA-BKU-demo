exports.translateImage = (req, res) => {
  const { imageName } = req.body;
  console.log(`Received imageName: ${imageName}`);
  res.send('morgen wird es überwiegend sonnig');
};
