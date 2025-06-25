const express = require('express');
const router = express.Router();

// 基礎健康檢查
router.get('/', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development',
    version: '1.0.0'
  });
});

// 詳細健康檢查
router.get('/detailed', async (req, res) => {
  const healthStatus = {
    status: 'OK',
    timestamp: new Date().toISOString(),
    services: {}
  };

  // 檢查 OpenAI API 配置
  healthStatus.services.openai = {
    configured: !!process.env.OPENAI_API_KEY,
    status: process.env.OPENAI_API_KEY ? 'available' : 'not_configured'
  };

  // 檢查內存使用情況
  const memUsage = process.memoryUsage();
  healthStatus.system = {
    memory: {
      used: Math.round(memUsage.heapUsed / 1024 / 1024),
      total: Math.round(memUsage.heapTotal / 1024 / 1024),
      unit: 'MB'
    },
    uptime: Math.round(process.uptime()),
    node_version: process.version
  };

  // 檢查數據存儲
  try {
    const fs = require('fs').promises;
    const path = require('path');
    const dataDir = path.join(__dirname, '../../data');
    
    await fs.access(dataDir);
    healthStatus.services.storage = {
      status: 'available',
      type: 'json_files',
      location: dataDir
    };
  } catch (error) {
    healthStatus.services.storage = {
      status: 'error',
      error: 'Data directory not accessible'
    };
  }

  res.json(healthStatus);
});

module.exports = router;