const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
const translateRoute = require('./routes/signLanguageTranslateRoute');
app.use('/api/sl-translate', translateRoute);

const googleTranslateRoute = require('./routes/googleTranslateRoute');
app.use('/api/google-translate', googleTranslateRoute);

const getVideoRoute = require('./routes/getVideoRoute');
app.use('/api/get-video', getVideoRoute);

app.get('/', (req, res) => {
  res.send('Hello World!');
});

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
