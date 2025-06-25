const express = require('express');
const OpenAIService = require('../services/openaiService');
const DataService = require('../services/dataService');

const router = express.Router();
const openaiService = new OpenAIService();
const dataService = new DataService();

// 獲取所有團隊
router.get('/', async (req, res) => {
  try {
    console.log('📋 獲取團隊列表');
    const teams = await dataService.getAllTeams();
    
    res.json({ 
      success: true, 
      data: teams,
      total: teams.length
    });
  } catch (error) {
    console.error('❌ 獲取團隊列表失敗:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

// 獲取特定團隊詳情
router.get('/:id', async (req, res) => {
  try {
    const teamId = req.params.id;
    console.log(`👥 獲取團隊詳情: ${teamId}`);
    
    const team = await dataService.getTeam(teamId);
    const latestAnalysis = await dataService.getLatestAnalysis('team', teamId);
    
    // 獲取團隊成員詳細資料
    const membersDetails = [];
    if (team.members && Array.isArray(team.members)) {
      for (const member of team.members) {
        try {
          if (member.id) {
            const employeeDetail = await dataService.getEmployee(member.id);
            membersDetails.push({
              ...member,
              details: employeeDetail
            });
          } else {
            membersDetails.push(member);
          }
        } catch (error) {
          // 如果找不到員工詳情，保留基本資訊
          membersDetails.push(member);
        }
      }
    }
    
    res.json({ 
      success: true, 
      data: {
        team: {
          ...team,
          membersDetails
        },
        latestAnalysis
      }
    });
  } catch (error) {
    console.error('❌ 獲取團隊詳情失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Team not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 分析特定團隊
router.post('/:id/analyze', async (req, res) => {
  try {
    const teamId = req.params.id;
    console.log(`🔍 開始團隊分析: ${teamId}`);
    
    // 獲取團隊基本資料
    const team = await dataService.getTeam(teamId);
    
    // 獲取團隊成員詳細資料
    const membersWithDetails = [];
    if (team.members && Array.isArray(team.members)) {
      for (const member of team.members) {
        try {
          if (member.id) {
            const employeeDetail = await dataService.getEmployee(member.id);
            membersWithDetails.push({
              ...member,
              ...employeeDetail
            });
          } else {
            membersWithDetails.push(member);
          }
        } catch (error) {
          console.warn(`⚠️ 無法獲取成員 ${member.id} 的詳細資料:`, error.message);
          membersWithDetails.push(member);
        }
      }
    }
    
    // 合併前端提供的額外分析參數
    const analysisData = {
      ...team,
      members: membersWithDetails,
      ...req.body,
      // 確保必要欄位存在
      analysisDepth: req.body.analysisDepth || 'standard',
      analysisPeriod: req.body.analysisPeriod || '3months',
      collaborationMode: req.body.collaborationMode || team.collaborationMode,
      teamPerformance: req.body.teamPerformance || team.teamPerformance,
      collaborationEfficiency: req.body.collaborationEfficiency || team.collaborationEfficiency
    };

    console.log(`📊 分析參數: ${analysisData.analysisDepth}, 週期: ${analysisData.analysisPeriod}`);

    // 執行AI分析
    const analysisResult = await openaiService.analyzeTeam(analysisData);
    
    // 儲存分析結果
    const savedAnalysis = await dataService.saveAnalysis(
      'team', 
      teamId, 
      analysisResult,
      {
        analysisDepth: analysisData.analysisDepth,
        analysisPeriod: analysisData.analysisPeriod,
        memberCount: team.memberCount,
        requestId: req.headers['x-request-id'] || 'unknown'
      }
    );
    
    console.log(`✅ 團隊分析完成: ${teamId}, 來源: ${analysisResult.source}`);
    
    res.json({
      success: true,
      data: {
        team: team,
        analysis: analysisResult.data,
        metadata: {
          analyzedAt: savedAnalysis.metadata.timestamp,
          source: analysisResult.source,
          analysisId: savedAnalysis.id,
          parameters: {
            analysisDepth: analysisData.analysisDepth,
            analysisPeriod: analysisData.analysisPeriod,
            memberCount: team.memberCount
          }
        }
      }
    });
  } catch (error) {
    console.error('❌ 團隊分析失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Team not found' 
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

// 獲取團隊分析歷史
router.get('/:id/history', async (req, res) => {
  try {
    const teamId = req.params.id;
    const limit = parseInt(req.query.limit) || 10;
    
    console.log(`📚 獲取團隊分析歷史: ${teamId}, 限制: ${limit}`);
    
    // 驗證團隊存在
    await dataService.getTeam(teamId);
    
    const history = await dataService.getAnalysisHistory('team', teamId, limit);
    
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
        error: 'Team not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 獲取團隊成員績效概覽
router.get('/:id/members-overview', async (req, res) => {
  try {
    const teamId = req.params.id;
    console.log(`👥 獲取團隊成員績效概覽: ${teamId}`);
    
    const team = await dataService.getTeam(teamId);
    
    const membersOverview = [];
    if (team.members && Array.isArray(team.members)) {
      for (const member of team.members) {
        try {
          if (member.id) {
            const employeeDetail = await dataService.getEmployee(member.id);
            const latestAnalysis = await dataService.getLatestAnalysis('employee', member.id);
            
            membersOverview.push({
              id: member.id,
              name: member.name,
              role: member.role,
              position: employeeDetail.position,
              experience: employeeDetail.experience,
              skills: employeeDetail.skills,
              latestAnalysis: latestAnalysis ? {
                overallScore: latestAnalysis.analysis.overallScore,
                analyzedAt: latestAnalysis.metadata.timestamp,
                source: latestAnalysis.metadata.source
              } : null
            });
          }
        } catch (error) {
          console.warn(`⚠️ 無法獲取成員 ${member.id} 的績效數據:`, error.message);
          membersOverview.push({
            id: member.id,
            name: member.name,
            role: member.role,
            error: 'Data not available'
          });
        }
      }
    }
    
    res.json({ 
      success: true, 
      data: {
        teamId,
        teamName: team.name,
        memberCount: team.memberCount,
        members: membersOverview
      }
    });
  } catch (error) {
    console.error('❌ 獲取團隊成員概覽失敗:', error);
    
    if (error.message.includes('not found')) {
      res.status(404).json({ 
        success: false, 
        error: 'Team not found' 
      });
    } else {
      res.status(500).json({ 
        success: false, 
        error: error.message 
      });
    }
  }
});

// 比較多個團隊 (可選功能)
router.post('/compare', async (req, res) => {
  try {
    const { teamIds } = req.body;
    
    if (!Array.isArray(teamIds) || teamIds.length < 2) {
      return res.status(400).json({
        success: false,
        error: 'teamIds must be an array with at least 2 team IDs'
      });
    }

    console.log(`📊 比較團隊: ${teamIds.length} 個團隊`);

    const comparisons = [];
    const errors = [];

    for (const teamId of teamIds) {
      try {
        const team = await dataService.getTeam(teamId);
        const latestAnalysis = await dataService.getLatestAnalysis('team', teamId);
        
        comparisons.push({
          teamId,
          teamName: team.name,
          department: team.department,
          memberCount: team.memberCount,
          analysis: latestAnalysis ? latestAnalysis.analysis : null,
          analyzedAt: latestAnalysis ? latestAnalysis.metadata.timestamp : null
        });

      } catch (error) {
        console.error(`❌ 獲取團隊 ${teamId} 失敗:`, error);
        errors.push({
          teamId,
          error: error.message
        });
      }
    }

    console.log(`✅ 團隊比較完成: ${comparisons.length} 成功, ${errors.length} 失敗`);

    res.json({
      success: true,
      data: {
        comparisons,
        errors,
        summary: {
          total: teamIds.length,
          successful: comparisons.length,
          failed: errors.length
        }
      }
    });

  } catch (error) {
    console.error('❌ 團隊比較失敗:', error);
    res.status(500).json({ 
      success: false, 
      error: error.message 
    });
  }
});

module.exports = router;