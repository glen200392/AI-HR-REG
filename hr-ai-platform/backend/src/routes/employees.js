const express = require('express');
const OpenAIService = require('../services/openaiService');
const DataService = require('../services/dataService');

const router = express.Router();
const openaiService = new OpenAIService();
const dataService = new DataService();

// 獲取所有員工
router.get('/', async (req, res) => {
  try {
    console.log('📋 獲取員工列表');
    const employees = await dataService.getAllEmployees();
    
    res.json({ 
      success: true, 
      data: employees,
      total: employees.length
    });
  } catch (error) {
    console.error('❌ 獲取員工列表失敗:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 獲取特定員工詳情
router.get('/:id', async (req, res) => {
  try {
    const employeeId = req.params.id;
    console.log(`👤 獲取員工詳情: ${employeeId}`);
    
    const employee = await dataService.getEmployee(employeeId);
    const latestAnalysis = await dataService.getLatestAnalysis('employee', employeeId);
    
    res.json({ 
      success: true, 
      data: {
        employee,
        latestAnalysis
      }
    });
  } catch (error) {
    console.error('❌ 獲取員工詳情失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Employee not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 分析特定員工
router.post('/:id/analyze', async (req, res) => {
  try {
    const employeeId = req.params.id;
    console.log(`🔍 開始員工分析: ${employeeId}`);
    
    // 獲取員工基本資料
    const employee = await dataService.getEmployee(employeeId);
    
    // 合併前端提供的額外分析參數
    const analysisData = {
      ...employee,
      ...req.body,
      // 確保必要欄位存在
      analysisType: req.body.analysisType || 'comprehensive',
      timeRange: req.body.timeRange || '6months',
      recentPerformance: req.body.recentPerformance || employee.recentPerformance,
      feedback: req.body.feedback || employee.feedback,
      projectContribution: req.body.projectContribution || employee.projectContribution
    };

    console.log(`📊 分析參數: ${analysisData.analysisType}, 時間範圍: ${analysisData.timeRange}`);

    // 執行AI分析
    const analysisResult = await openaiService.analyzeEmployee(analysisData);
    
    // 儲存分析結果
    const savedAnalysis = await dataService.saveAnalysis(
      'employee', 
      employeeId, 
      analysisResult,
      {
        analysisType: analysisData.analysisType,
        timeRange: analysisData.timeRange,
        requestId: req.headers['x-request-id'] || 'unknown'
      }
    );
    
    console.log(`✅ 員工分析完成: ${employeeId}, 來源: ${analysisResult.source}`);
    
    res.json({
      success: true,
      data: {
        employee: employee,
        analysis: analysisResult.data,
        metadata: {
          analyzedAt: savedAnalysis.metadata.timestamp,
          source: analysisResult.source,
          analysisId: savedAnalysis.id,
          parameters: {
            analysisType: analysisData.analysisType,
            timeRange: analysisData.timeRange
          }
        }
      }
    });
  } catch (error) {
    console.error('❌ 員工分析失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Employee not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message,
        details: process.env.NODE_ENV === 'development' ? error.stack : undefined
      });
    }
  }
});

// 獲取員工分析歷史
router.get('/:id/history', async (req, res) => {
  try {
    const employeeId = req.params.id;
    const limit = parseInt(req.query.limit) || 10;
    
    console.log(`📚 獲取員工分析歷史: ${employeeId}, 限制: ${limit}`);
    
    // 驗證員工存在
    await dataService.getEmployee(employeeId);
    
    const history = await dataService.getAnalysisHistory('employee', employeeId, limit);
    
    res.json({ 
      success: true, 
      data: history,
      total: history.length
    });
  } catch (error) {
    console.error('❌ 獲取分析歷史失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Employee not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 新增員工
router.post('/', async (req, res) => {
  try {
    console.log('➕ 新增員工');
    
    // 基本驗證
    const { name, position, department, email } = req.body;
    if (!name || !position || !department || !email) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: name, position, department, email'
      });
    }

    const newEmployee = await dataService.addEmployee(req.body);
    
    console.log(`✅ 員工新增成功: ${newEmployee.name} (${newEmployee.id})`);
    
    res.status(201).json({
      success: true,
      data: newEmployee
    });
  } catch (error) {
    console.error('❌ 新增員工失敗:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 更新員工資料
router.put('/:id', async (req, res) => {
  try {
    const employeeId = req.params.id;
    console.log(`📝 更新員工資料: ${employeeId}`);
    
    const updatedEmployee = await dataService.updateEmployee(employeeId, req.body);
    
    console.log(`✅ 員工資料更新成功: ${updatedEmployee.name}`);
    
    res.json({
      success: true,
      data: updatedEmployee
    });
  } catch (error) {
    console.error('❌ 更新員工資料失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Employee not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 批量分析員工 (可選功能)
router.post('/batch-analyze', async (req, res) => {
  try {
    const { employeeIds, analysisType = 'comprehensive', timeRange = '6months' } = req.body;
    
    if (!Array.isArray(employeeIds) || employeeIds.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'employeeIds must be a non-empty array'
      });
    }

    console.log(`🔍 批量分析員工: ${employeeIds.length} 人`);

    const results = [];
    const errors = [];

    for (const employeeId of employeeIds) {
      try {
        const employee = await dataService.getEmployee(employeeId);
        const analysisData = {
          ...employee,
          analysisType,
          timeRange
        };

        const analysisResult = await openaiService.analyzeEmployee(analysisData);
        
        await dataService.saveAnalysis('employee', employeeId, analysisResult, {
          batchAnalysis: true,
          analysisType,
          timeRange
        });

        results.push({
          employeeId,
          employee: employee.name,
          success: true,
          analysis: analysisResult.data,
          source: analysisResult.source
        });

      } catch (error) {
        console.error(`❌ 分析員工 ${employeeId} 失敗:`, error);
        errors.push({
          employeeId,
          error: error.message
        });
      }
    }

    console.log(`✅ 批量分析完成: ${results.length} 成功, ${errors.length} 失敗`);

    res.json({
      success: true,
      data: {
        successful: results,
        failed: errors,
        summary: {
          total: employeeIds.length,
          successful: results.length,
          failed: errors.length
        }
      }
    });

  } catch (error) {
    console.error('❌ 批量分析失敗:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;