const OpenAI = require('openai');

class OpenAIService {
  constructor() {
    if (!process.env.OPENAI_API_KEY) {
      console.warn('⚠️ OpenAI API key not configured. Falling back to mock responses.');
      this.client = null;
    } else {
      this.client = new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
    }
    
    this.model = process.env.AI_MODEL || 'gpt-4';
    this.maxTokens = parseInt(process.env.AI_MAX_TOKENS) || 1500;
    this.temperature = parseFloat(process.env.AI_TEMPERATURE) || 0.7;
  }

  async analyzeEmployee(employeeData) {
    console.log(`🤖 開始分析員工: ${employeeData.name}`);
    
    if (!this.client) {
      console.log('📝 使用模擬AI回應 (OpenAI未配置)');
      return this.getMockEmployeeAnalysis(employeeData);
    }

    const prompt = this.buildEmployeePrompt(employeeData);
    
    try {
      console.log('🚀 調用 OpenAI API...');
      const startTime = Date.now();
      
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: [
          {
            role: "system",
            content: this.getEmployeeSystemPrompt()
          },
          {
            role: "user", 
            content: prompt
          }
        ],
        max_tokens: this.maxTokens,
        temperature: this.temperature
      });

      const duration = Date.now() - startTime;
      console.log(`✅ OpenAI API 回應完成 (${duration}ms)`);

      return this.parseEmployeeAnalysis(response.choices[0].message.content);
    } catch (error) {
      console.error('❌ OpenAI API 錯誤:', error.message);
      return this.getFallbackEmployeeAnalysis(employeeData);
    }
  }

  async analyzeTeam(teamData) {
    console.log(`🤖 開始分析團隊: ${teamData.name}`);
    
    if (!this.client) {
      console.log('📝 使用模擬AI回應 (OpenAI未配置)');
      return this.getMockTeamAnalysis(teamData);
    }

    const prompt = this.buildTeamPrompt(teamData);
    
    try {
      console.log('🚀 調用 OpenAI API...');
      const startTime = Date.now();
      
      const response = await this.client.chat.completions.create({
        model: this.model,
        messages: [
          {
            role: "system",
            content: this.getTeamSystemPrompt()
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: this.maxTokens,
        temperature: this.temperature
      });

      const duration = Date.now() - startTime;
      console.log(`✅ OpenAI API 回應完成 (${duration}ms)`);

      return this.parseTeamAnalysis(response.choices[0].message.content);
    } catch (error) {
      console.error('❌ OpenAI API 錯誤:', error.message);
      return this.getFallbackTeamAnalysis(teamData);
    }
  }

  getEmployeeSystemPrompt() {
    return `你是一位專業的HR分析專家，具備以下專長：
1. 員工績效評估與分析
2. 職涯發展規劃
3. 技能評估與培訓建議
4. 人才保留策略

請基於提供的員工資料，進行深度分析並提供專業建議。
回應必須是有效的JSON格式，包含以下結構：
{
  "overallScore": 數字(1-10),
  "performanceScore": 數字(1-10),
  "skillsScore": 數字(1-10),
  "potentialScore": 數字(1-10),
  "strengths": [字串數組],
  "improvements": [字串數組],
  "developmentPlan": "字串",
  "riskAssessment": "字串",
  "careerPath": "字串"
}

確保分析客觀、專業且具有建設性。`;
  }

  getTeamSystemPrompt() {
    return `你是一位團隊動力分析專家，專精於：
1. 團隊協作模式分析
2. 組織行為研究
3. 團隊效能優化
4. 衝突預防與解決

請基於提供的團隊資料，分析團隊動力並提供優化建議。
回應必須是有效的JSON格式，包含以下結構：
{
  "teamScore": 數字(1-10),
  "collaborationScore": 數字(1-10),
  "communicationScore": 數字(1-10),
  "productivityScore": 數字(1-10),
  "strengths": [字串數組],
  "risks": [字串數組],
  "suggestions": [字串數組],
  "actionPlan": [{"title": "字串", "description": "字串", "timeline": "字串"}]
}

確保分析基於團隊動力學理論，提供實用且可執行的建議。`;
  }

  buildEmployeePrompt(employee) {
    return `請分析以下員工的詳細資料：

基本資訊：
- 姓名：${employee.name}
- 職位：${employee.position}
- 部門：${employee.department}
- 工作年資：${employee.experience || '未提供'}年
- 入職日期：${employee.joinDate || '未提供'}

技能與能力：
- 核心技能：${Array.isArray(employee.skills) ? employee.skills.join(', ') : '未提供'}
- 專業領域：${employee.specialization || employee.position}

績效表現：
- 近期表現：${employee.recentPerformance || '穩定表現，持續成長'}
- 團隊反饋：${employee.feedback || '積極參與，協作良好'}
- 項目貢獻：${employee.projectContribution || '按時完成任務，品質良好'}

分析類型：${employee.analysisType || '綜合分析'}
時間範圍：${employee.timeRange || '近6個月'}

請提供全面的員工分析，包括績效評估、發展潛力、技能強弱項分析，以及具體的發展建議和風險評估。`;
  }

  buildTeamPrompt(team) {
    const membersList = Array.isArray(team.members) 
      ? team.members.map(m => `${m.name} (${m.role || m.position})`).join(', ')
      : '團隊成員資訊未提供';

    return `請分析以下團隊的詳細資料：

團隊基本資訊：
- 團隊名稱：${team.name}
- 所屬部門：${team.department || '未提供'}
- 成員數量：${team.memberCount || team.members?.length || '未知'}
- 團隊類型：${team.teamType || '專案團隊'}

團隊組成：
- 成員列表：${membersList}
- 領導者：${team.leader || '未指定'}
- 團隊經驗：${team.teamExperience || '2-3年'}

工作模式：
- 協作方式：${team.collaborationMode || '混合工作模式'}
- 溝通頻率：${team.communicationFrequency || '每日站會 + 週會'}
- 決策模式：${team.decisionMaking || '共識決策'}

績效狀況：
- 近期項目：${team.recentProjects || '持續進行多個專案'}
- 團隊績效：${team.teamPerformance || '整體表現良好'}
- 協作效率：${team.collaborationEfficiency || '高效協作'}

分析深度：${team.analysisDepth || '標準分析'}
分析週期：${team.analysisPeriod || '近3個月'}

請提供團隊動力分析，包括協作效率、溝通模式、潛在風險識別，以及具體的團隊優化建議和行動計劃。`;
  }

  parseEmployeeAnalysis(content) {
    try {
      // 嘗試直接解析JSON
      const cleanContent = this.extractJSON(content);
      const analysis = JSON.parse(cleanContent);
      
      return {
        success: true,
        data: this.validateEmployeeAnalysis(analysis),
        source: 'openai'
      };
    } catch (error) {
      console.warn('JSON解析失敗，嘗試文本解析:', error.message);
      return {
        success: true,
        data: this.parseEmployeeTextResponse(content),
        source: 'openai-parsed'
      };
    }
  }

  parseTeamAnalysis(content) {
    try {
      const cleanContent = this.extractJSON(content);
      const analysis = JSON.parse(cleanContent);
      
      return {
        success: true,
        data: this.validateTeamAnalysis(analysis),
        source: 'openai'
      };
    } catch (error) {
      console.warn('JSON解析失敗，嘗試文本解析:', error.message);
      return {
        success: true,
        data: this.parseTeamTextResponse(content),
        source: 'openai-parsed'
      };
    }
  }

  extractJSON(content) {
    // 移除可能的markdown代碼塊標記
    const jsonMatch = content.match(/```(?:json)?\s*(\{[\s\S]*\})\s*```/);
    if (jsonMatch) {
      return jsonMatch[1];
    }
    
    // 嘗試找到JSON對象
    const objectMatch = content.match(/\{[\s\S]*\}/);
    if (objectMatch) {
      return objectMatch[0];
    }
    
    return content;
  }

  validateEmployeeAnalysis(analysis) {
    return {
      overallScore: this.validateScore(analysis.overallScore),
      performanceScore: this.validateScore(analysis.performanceScore),
      skillsScore: this.validateScore(analysis.skillsScore),
      potentialScore: this.validateScore(analysis.potentialScore),
      strengths: Array.isArray(analysis.strengths) ? analysis.strengths : ["技能表現良好"],
      improvements: Array.isArray(analysis.improvements) ? analysis.improvements : ["持續學習新技能"],
      developmentPlan: analysis.developmentPlan || "建議制定個人發展計劃",
      riskAssessment: analysis.riskAssessment || "整體風險較低",
      careerPath: analysis.careerPath || "建議逐步提升專業能力"
    };
  }

  validateTeamAnalysis(analysis) {
    return {
      teamScore: this.validateScore(analysis.teamScore),
      collaborationScore: this.validateScore(analysis.collaborationScore),
      communicationScore: this.validateScore(analysis.communicationScore),
      productivityScore: this.validateScore(analysis.productivityScore),
      strengths: Array.isArray(analysis.strengths) ? analysis.strengths : ["團隊合作良好"],
      risks: Array.isArray(analysis.risks) ? analysis.risks : ["需要關注工作負荷"],
      suggestions: Array.isArray(analysis.suggestions) ? analysis.suggestions : ["加強團隊溝通"],
      actionPlan: Array.isArray(analysis.actionPlan) ? analysis.actionPlan : [
        {title: "提升協作效率", description: "定期檢討工作流程", timeline: "1個月"}
      ]
    };
  }

  validateScore(score) {
    const num = parseFloat(score);
    if (isNaN(num)) return 7.5;
    return Math.max(1, Math.min(10, num));
  }

  parseEmployeeTextResponse(content) {
    // 簡單的文本解析邏輯
    return {
      overallScore: 8.0,
      performanceScore: 8.2,
      skillsScore: 7.8,
      potentialScore: 8.5,
      strengths: ["基於AI分析的優勢識別"],
      improvements: ["基於AI分析的改進建議"],
      developmentPlan: content.slice(0, 200) + "...",
      riskAssessment: "需要進一步評估",
      careerPath: "建議諮詢專業顧問"
    };
  }

  parseTeamTextResponse(content) {
    return {
      teamScore: 8.0,
      collaborationScore: 8.2,
      communicationScore: 7.5,
      productivityScore: 8.3,
      strengths: ["基於AI分析的團隊優勢"],
      risks: ["需要關注的潛在風險"],
      suggestions: ["AI生成的優化建議"],
      actionPlan: [
        {title: "團隊優化計劃", description: content.slice(0, 100) + "...", timeline: "2-4週"}
      ]
    };
  }

  getMockEmployeeAnalysis(employee) {
    return {
      success: true,
      data: {
        overallScore: 8.2,
        performanceScore: 8.5,
        skillsScore: 7.8,
        potentialScore: 8.7,
        strengths: [
          `在${employee.position}領域表現突出`,
          "學習能力強，適應性好",
          "團隊協作積極主動",
          "問題解決能力優秀"
        ],
        improvements: [
          "可進一步提升技術深度",
          "建議加強跨部門協作經驗",
          "可考慮承擔更多領導責任"
        ],
        developmentPlan: `建議${employee.name}在接下來6個月內重點發展技術領導力，參與更多跨功能項目，並考慮進修相關認證課程。`,
        riskAssessment: "整體風險較低，建議定期關注職涯發展需求和工作滿意度。",
        careerPath: `適合往資深${employee.position}或技術管理方向發展。`
      },
      source: 'mock'
    };
  }

  getMockTeamAnalysis(team) {
    return {
      success: true,
      data: {
        teamScore: 8.4,
        collaborationScore: 8.7,
        communicationScore: 8.1,
        productivityScore: 8.6,
        strengths: [
          "團隊凝聚力強，協作氛圍良好",
          "技能互補性高，分工明確",
          "溝通效率佳，決策速度快",
          "持續學習意願強"
        ],
        risks: [
          "關鍵成員工作負荷可能過重",
          "缺乏備援人員安排",
          "跨部門協作經驗相對不足"
        ],
        suggestions: [
          "建立知識分享機制",
          "定期進行工作負荷評估",
          "增加跨部門合作機會",
          "設立團隊導師制度"
        ],
        actionPlan: [
          {
            title: "知識分享機制建立",
            description: "每週安排技術分享會，促進團隊知識交流",
            timeline: "2週內啟動"
          },
          {
            title: "工作負荷優化",
            description: "評估並重新分配工作任務，避免單點風險",
            timeline: "1個月內完成"
          },
          {
            title: "跨部門協作計劃",
            description: "安排與其他部門的聯合項目或交流活動",
            timeline: "2個月內實施"
          }
        ]
      },
      source: 'mock'
    };
  }

  getFallbackEmployeeAnalysis(employee) {
    console.log('🔄 使用降級員工分析');
    return this.getMockEmployeeAnalysis(employee);
  }

  getFallbackTeamAnalysis(team) {
    console.log('🔄 使用降級團隊分析');
    return this.getMockTeamAnalysis(team);
  }
}

module.exports = OpenAIService;