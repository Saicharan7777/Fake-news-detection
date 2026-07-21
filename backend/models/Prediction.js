const mongoose = require('mongoose');

const PredictionSchema = new mongoose.Schema({
  newsText: {
    type: String,
    required: true,
    trim: true
  },
  predictionResult: {
    type: String,
    required: true,
    enum: ['Real', 'Fake']
  },
  confidenceScore: {
    type: Number,
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Prediction', PredictionSchema);
