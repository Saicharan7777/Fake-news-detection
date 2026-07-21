require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./db');
const predictRoutes = require('./routes/predict');

// Attempt MongoDB connection but don't block startup if it fails
connectDB().catch((err) => {
  console.warn(`MongoDB not available — predictions will still work but won't be saved. (${err.message})`);
});

const app = express();

// Allow requests from local dev and all deployed frontends
app.use(cors({
  origin: [
    'http://localhost:5173',
    'https://fake-news-detection-k6dk.onrender.com',
    'https://fake-news-detection-plum.vercel.app'
  ],
  methods: ['GET', 'POST'],
  credentials: true
}));
app.use(express.json());

// Mount routes at root so /predict works directly
app.use(predictRoutes);

app.get('/', (req, res) => {
  res.json({ app: 'Fake News Detector', status: 'running' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', message: 'Fake News Detector server is running.' });
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
