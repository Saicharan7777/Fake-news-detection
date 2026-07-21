const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const mongoURI = process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/fake-news-detector';
    const conn = await mongoose.connect(mongoURI);
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error(`Database connection failed: ${error.message}`);
    console.error(`Please verify your MongoDB Atlas IP Whitelist settings (Network Access in Atlas Dashboard).`);
  }
};

module.exports = connectDB;
