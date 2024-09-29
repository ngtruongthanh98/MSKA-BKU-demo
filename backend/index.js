const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;

// Middleware
app.use(cors()); // Enable CORS
app.use(express.json());

// Routes
const translateRoute = require('./routes/signLanguageTranslateRoute');
app.use('/api/sl-translate', translateRoute);

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
