const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const morgan = require('morgan');
require('dotenv').config();

// 路由導入
const employeeRoutes = require('./routes/employees');
const teamRoutes = require('./routes/teams');
const healthRoutes = require('./routes/health');

const app = express();

// 安全中間件
app.use(helmet());

// CORS 配置
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));

// 請求限制
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 15 * 60 * 1000, // 15分鐘
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // 限制每個IP在窗口時間內最多100個請求
  message: {
    error: 'Too many requests from this IP, please try again later.',
    retryAfter: '15 minutes'
  }
});
app.use('/api/', limiter);

// 日誌中間件
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('combined'));
}

// 請求解析中間件
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// API 路由
app.use('/api/employees', employeeRoutes);
app.use('/api/teams', teamRoutes);
app.use('/health', healthRoutes);

// 根路由
app.get('/', (req, res) => {
  res.json({
    message: 'HR AI Platform API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      employees: '/api/employees',
      teams: '/api/teams'
    }
  });
});

// 404 處理
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: 'API endpoint not found',
    path: req.originalUrl
  });
});

// 全局錯誤處理
app.use((err, req, res, next) => {
  console.error('Global error handler:', err);
  
  // 開發環境顯示詳細錯誤
  const isDev = process.env.NODE_ENV === 'development';
  
  res.status(err.status || 500).json({
    success: false,
    error: err.message || 'Internal server error',
    ...(isDev && { stack: err.stack })
  });
});

const PORT = process.env.PORT || 3001;

if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log(`🚀 HR AI API Server running on port ${PORT}`);
    console.log(`📊 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`🔗 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:5173'}`);
    console.log(`🤖 OpenAI API: ${process.env.OPENAI_API_KEY ? '✅ Configured' : '❌ Missing'}`);
  });
}

module.exports = app;