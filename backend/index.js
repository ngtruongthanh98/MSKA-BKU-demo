const express = require('express');
const app = express();
const port = 3000;

// Middleware
app.use(express.json());

// Routes
const translateRoute = require('./routes/translateRoute');
app.use('/api/translate', translateRoute);

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
