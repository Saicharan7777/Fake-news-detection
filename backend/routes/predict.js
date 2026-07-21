const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');
const Prediction = require('../models/Prediction');

router.post('/predict', async (req, res) => {
  try {
    const { newsText } = req.body;

    if (!newsText || typeof newsText !== 'string' || newsText.trim().length === 0) {
      return res.status(400).json({ error: 'Please provide valid news text for analysis.' });
    }

    const pythonScript = path.join(__dirname, '..', 'python', 'predict.py');
    const pythonCwd = path.join(__dirname, '..', 'python');

    // Use python3 on Linux (Render) and python on Windows
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    const pyProcess = spawn(pythonCmd, [pythonScript], {
      cwd: pythonCwd,
      env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });

    let stdoutData = '';
    let stderrData = '';

    pyProcess.stdin.write(newsText);
    pyProcess.stdin.end();

    pyProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    pyProcess.on('close', async (code) => {
      if (code !== 0) {
        console.error(`Python script exited with code ${code}. Error: ${stderrData}`);
        return res.status(500).json({ 
          error: 'Machine Learning prediction failed.', 
          details: stderrData || 'Unknown Python execution error.' 
        });
      }

      try {
        const result = JSON.parse(stdoutData.trim());

        if (result.error) {
          return res.status(400).json({ error: result.error });
        }

        let savedToDb = false;
        let savedPrediction = null;

        try {
          const newPrediction = new Prediction({
            newsText: newsText.trim(),
            predictionResult: result.prediction,
            confidenceScore: result.confidence
          });
          savedPrediction = await newPrediction.save();
          savedToDb = true;
        } catch (dbError) {
          console.error(`Failed to save prediction to MongoDB Atlas: ${dbError.message}`);
        }

        return res.json({
          _id: savedPrediction ? savedPrediction._id : null,
          newsText: newsText.trim(),
          predictionResult: result.prediction,
          confidenceScore: result.confidence,
          timestamp: savedPrediction ? savedPrediction.timestamp : new Date(),
          savedToDb
        });

      } catch (parseError) {
        console.error(`JSON Parse Error: ${parseError.message}. Output was: ${stdoutData}`);
        return res.status(500).json({ 
          error: 'Failed to process the prediction output.',
          details: stdoutData
        });
      }
    });

  } catch (error) {
    console.error(`Server error in predict route: ${error.message}`);
    return res.status(500).json({ error: 'Server error processing news analysis.' });
  }
});

router.get('/history', async (req, res) => {
  try {
    const history = await Prediction.find()
      .sort({ timestamp: -1 })
      .limit(15);
      
    return res.json(history);
  } catch (error) {
    console.error(`Server error fetching history: ${error.message}`);
    return res.status(500).json({ error: 'Server error fetching prediction history.' });
  }
});

module.exports = router;
