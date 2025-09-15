const express = require('express');
const cors = require('cors');
const axios = require('axios');
const dotenv = require('dotenv');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8000';

// Middleware
app.use(cors());
app.use(express.json());

// Proxy requests to Python backend
app.use('/api', async (req, res) => {
  try {
    const response = await axios({
      method: req.method,
      url: `${PYTHON_BACKEND_URL}${req.path}`,
      data: req.body,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    res.json(response.data);
  } catch (error) {
    console.error('Proxy error:', error.message);
    res.status(error.response?.status || 500).json({
      error: error.response?.data?.detail || 'Internal server error'
    });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    backend_url: PYTHON_BACKEND_URL
  });
});

// Serve static files in production
if (process.env.NODE_ENV === 'production') {
  app.use(express.static('client/build'));
  
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
  console.log(`Proxying to Python backend at ${PYTHON_BACKEND_URL}`);
});

