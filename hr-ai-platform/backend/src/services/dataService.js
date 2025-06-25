const fs = require('fs').promises;
const path = require('path');
const { v4: uuidv4 } = require('uuid');

class DataService {
  constructor() {
    this.dataDir = path.join(__dirname, '../../data');
    this.employeesFile = path.join(this.dataDir, 'employees.json');
    this.teamsFile = path.join(this.dataDir, 'teams.json');
    this.analysesFile = path.join(this.dataDir, 'analyses.json');
    
    this.ensureDataDirectory();
  }

  async ensureDataDirectory() {
    try {
      await fs.access(this.dataDir);
      console.log('📁 數據目錄已存在');
    } catch {
      await fs.mkdir(this.dataDir, { recursive: true });
      console.log('📁 創建數據目錄');
    }
  }

  // 員工數據管理
  async getAllEmployees() {
    try {
      const data = await fs.readFile(this.employeesFile, 'utf8');
      console.log('📖 載入員工數據');
      return JSON.parse(data);
    } catch (error) {
      console.log('📝 使用默認員工數據');
      const defaultData = this.getDefaultEmployees();
      await this.saveEmployees(defaultData);
      return defaultData;
    }
  }

  async getEmployee(id) {
    const employees = await this.getAllEmployees();
    const employee = employees.find(emp => emp.id === id);
    if (!employee) {
      throw new Error(`Employee with id ${id} not found`);
    }
    return employee;
  }

  async saveEmployees(employees) {
    await fs.writeFile(this.employeesFile, JSON.stringify(employees, null, 2));
    console.log('💾 保存員工數據');
  }

  async addEmployee(employeeData) {
    const employees = await this.getAllEmployees();
    const newEmployee = {
      id: uuidv4(),
      ...employeeData,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    
    employees.push(newEmployee);
    await this.saveEmployees(employees);
    
    return newEmployee;
  }

  async updateEmployee(id, updates) {
    const employees = await this.getAllEmployees();
    const index = employees.findIndex(emp => emp.id === id);
    
    if (index === -1) {
      throw new Error(`Employee with id ${id} not found`);
    }
    
    employees[index] = {
      ...employees[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };
    
    await this.saveEmployees(employees);
    return employees[index];
  }

  // 團隊數據管理
  async getAllTeams() {
    try {
      const data = await fs.readFile(this.teamsFile, 'utf8');
      console.log('📖 載入團隊數據');
      return JSON.parse(data);
    } catch (error) {
      console.log('📝 使用默認團隊數據');
      const defaultData = this.getDefaultTeams();
      await this.saveTeams(defaultData);
      return defaultData;
    }
  }

  async getTeam(id) {
    const teams = await this.getAllTeams();
    const team = teams.find(t => t.id === id);
    if (!team) {
      throw new Error(`Team with id ${id} not found`);
    }
    return team;
  }

  async saveTeams(teams) {
    await fs.writeFile(this.teamsFile, JSON.stringify(teams, null, 2));
    console.log('💾 保存團隊數據');
  }

  // 分析記錄管理
  async saveAnalysis(type, targetId, analysis, metadata = {}) {
    const analysisRecord = {
      id: uuidv4(),
      type, // 'employee' 或 'team'
      targetId,
      analysis: analysis.data,
      metadata: {
        source: analysis.source,
        success: analysis.success,
        timestamp: new Date().toISOString(),
        ...metadata
      }
    };

    let analyses = [];
    try {
      const data = await fs.readFile(this.analysesFile, 'utf8');
      analyses = JSON.parse(data);
    } catch {
      // 文件不存在，使用空數組
    }

    analyses.push(analysisRecord);

    // 保持最近1000條記錄
    if (analyses.length > 1000) {
      analyses = analyses.slice(-1000);
    }

    await fs.writeFile(this.analysesFile, JSON.stringify(analyses, null, 2));
    console.log(`💾 保存${type}分析記錄`);

    return analysisRecord;
  }

  async getAnalysisHistory(type, targetId, limit = 10) {
    try {
      const data = await fs.readFile(this.analysesFile, 'utf8');
      const analyses = JSON.parse(data);
      
      return analyses
        .filter(analysis => analysis.type === type && analysis.targetId === targetId)
        .sort((a, b) => new Date(b.metadata.timestamp) - new Date(a.metadata.timestamp))
        .slice(0, limit);
    } catch {
      return [];
    }
  }

  async getLatestAnalysis(type, targetId) {
    const history = await this.getAnalysisHistory(type, targetId, 1);
    return history[0] || null;
  }

  // 統計數據
  async getAnalysisStats() {
    try {
      const data = await fs.readFile(this.analysesFile, 'utf8');
      const analyses = JSON.parse(data);
      
      const now = new Date();
      const thisMonth = analyses.filter(a => {
        const analysisDate = new Date(a.metadata.timestamp);
        return analysisDate.getMonth() === now.getMonth() && 
               analysisDate.getFullYear() === now.getFullYear();
      });

      const thisWeek = analyses.filter(a => {
        const analysisDate = new Date(a.metadata.timestamp);
        const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        return analysisDate >= weekAgo;
      });

      return {
        total: analyses.length,
        thisMonth: thisMonth.length,
        thisWeek: thisWeek.length,
        byType: {
          employee: analyses.filter(a => a.type === 'employee').length,
          team: analyses.filter(a => a.type === 'team').length
        },
        bySource: {
          openai: analyses.filter(a => a.metadata.source === 'openai').length,
          mock: analyses.filter(a => a.metadata.source === 'mock').length,
          fallback: analyses.filter(a => a.metadata.source?.includes('fallback')).length
        }
      };
    } catch {
      return {
        total: 0,
        thisMonth: 0,
        thisWeek: 0,
        byType: { employee: 0, team: 0 },
        bySource: { openai: 0, mock: 0, fallback: 0 }
      };
    }
  }

  // 默認數據
  getDefaultEmployees() {
    return [
      {
        id: '1',
        name: '張小明',
        position: '前端工程師',
        department: '研發部',
        experience: 3,
        skills: ['JavaScript', 'Vue.js', 'React', 'CSS', 'HTML'],
        email: 'ming.zhang@company.com',
        joinDate: '2022-03-15',
        specialization: '前端開發',
        recentPerformance: '表現優秀，按時完成所有專案任務，代碼品質高',
        feedback: '同事評價積極，樂於助人，技術分享積極',
        projectContribution: '主導了公司官網重構項目，提升了40%的加載速度'
      },
      {
        id: '2',
        name: '李小華',
        position: '產品經理',
        department: '產品部',
        experience: 5,
        skills: ['產品規劃', '用戶研究', '數據分析', '項目管理', 'Agile'],
        email: 'hua.li@company.com',
        joinDate: '2020-07-01',
        specialization: '產品策略',
        recentPerformance: '成功推出3個新功能，用戶滿意度提升25%',
        feedback: '溝通能力強，能有效協調各部門資源',
        projectContribution: '負責用戶增長策略，月活躍用戶增長30%'
      },
      {
        id: '3',
        name: '王小美',
        position: 'UI設計師',
        department: '設計部',
        experience: 2,
        skills: ['Figma', 'Sketch', 'Adobe Creative Suite', 'Prototyping', 'User Research'],
        email: 'mei.wang@company.com',
        joinDate: '2022-09-01',
        specialization: '用戶介面設計',
        recentPerformance: '設計作品獲得團隊一致好評，設計效率持續提升',
        feedback: '創意思維活躍，對用戶體驗有敏銳洞察力',
        projectContribution: '重新設計了移動端界面，用戶體驗評分提升35%'
      },
      {
        id: '4',
        name: '陳小強',
        position: '後端工程師',
        department: '研發部',
        experience: 4,
        skills: ['Node.js', 'Python', 'Docker', 'MongoDB', 'Redis', 'AWS'],
        email: 'qiang.chen@company.com',
        joinDate: '2021-05-20',
        specialization: '後端架構',
        recentPerformance: '系統穩定性顯著提升，API響應時間優化50%',
        feedback: '技術能力強，對系統架構有深入理解',
        projectContribution: '主導微服務架構遷移，系統可擴展性大幅提升'
      },
      {
        id: '5',
        name: '林小莉',
        position: '數據分析師',
        department: '數據部',
        experience: 2,
        skills: ['Python', 'SQL', 'Tableau', 'Machine Learning', 'Statistics'],
        email: 'li.lin@company.com',
        joinDate: '2022-11-01',
        specialization: '數據科學',
        recentPerformance: '建立了多個關鍵業務指標的監控dashboard',
        feedback: '邏輯思維清晰，數據洞察能力強',
        projectContribution: '建立用戶行為預測模型，營銷效率提升40%'
      }
    ];
  }

  getDefaultTeams() {
    return [
      {
        id: '1',
        name: '前端開發團隊',
        department: '研發部',
        memberCount: 8,
        teamType: '技術團隊',
        leader: '張小明',
        members: [
          { id: '1', name: '張小明', role: '技術主管' },
          { id: '6', name: '劉小剛', role: '資深工程師' },
          { id: '7', name: '趙小雨', role: '工程師' },
          { id: '8', name: '錢小雪', role: '初級工程師' }
        ],
        collaborationMode: '敏捷開發，每日站會',
        communicationFrequency: '每日站會 + 週會 + 月度回顧',
        decisionMaking: '技術決策由團隊討論，產品決策配合產品部',
        recentProjects: ['官網重構', '移動端優化', '性能提升項目'],
        teamPerformance: '項目交付及時率95%，代碼質量持續提升',
        collaborationEfficiency: '團隊協作順暢，知識分享積極'
      },
      {
        id: '2',
        name: '後端開發團隊',
        department: '研發部',
        memberCount: 6,
        teamType: '技術團隊',
        leader: '陳小強',
        members: [
          { id: '4', name: '陳小強', role: '技術主管' },
          { id: '9', name: '孫小明', role: '資深工程師' },
          { id: '10', name: '周小華', role: '工程師' }
        ],
        collaborationMode: 'DevOps文化，持續集成部署',
        communicationFrequency: '每日站會 + 技術分享會',
        decisionMaking: '架構決策集體討論，執行分工明確',
        recentProjects: ['微服務架構遷移', 'API性能優化', '監控系統建設'],
        teamPerformance: '系統穩定性99.9%，API響應時間大幅改善',
        collaborationEfficiency: '跨團隊協作良好，技術文檔完善'
      },
      {
        id: '3',
        name: '產品設計團隊',
        department: '設計部',
        memberCount: 5,
        teamType: '創意團隊',
        leader: '王小美',
        members: [
          { id: '3', name: '王小美', role: '設計主管' },
          { id: '11', name: '鄭小樂', role: 'UX設計師' },
          { id: '12', name: '馮小悅', role: 'UI設計師' }
        ],
        collaborationMode: 'Design Thinking，用戶中心設計',
        communicationFrequency: '設計評審會 + 用戶研究分享',
        decisionMaking: '設計決策基於用戶研究和數據',
        recentProjects: ['移動端UI重設計', '用戶體驗優化', '設計系統建立'],
        teamPerformance: '設計交付及時率90%，用戶滿意度顯著提升',
        collaborationEfficiency: '與產品、開發團隊協作密切'
      },
      {
        id: '4',
        name: '數據分析團隊',
        department: '數據部',
        memberCount: 4,
        teamType: '分析團隊',
        leader: '林小莉',
        members: [
          { id: '5', name: '林小莉', role: '數據科學家' },
          { id: '13', name: '吳小智', role: '數據工程師' },
          { id: '14', name: '徐小慧', role: '業務分析師' }
        ],
        collaborationMode: '數據驅動決策，跨部門合作',
        communicationFrequency: '數據週報 + 業務討論會',
        decisionMaking: '基於數據分析結果提供建議',
        recentProjects: ['用戶行為分析', '業務指標監控', '預測模型建立'],
        teamPerformance: '分析報告準確率高，業務支援及時',
        collaborationEfficiency: '與各業務部門保持良好溝通'
      },
      {
        id: '5',
        name: '營運支援團隊',
        department: '營運部',
        memberCount: 7,
        teamType: '支援團隊',
        leader: '黃小亮',
        members: [
          { id: '15', name: '黃小亮', role: '營運主管' },
          { id: '16', name: '蔡小萍', role: '客服專員' },
          { id: '17', name: '許小強', role: '營運專員' }
        ],
        collaborationMode: '客戶服務導向，快速響應',
        communicationFrequency: '晨會 + 客戶反饋討論會',
        decisionMaking: '客戶需求優先，快速決策執行',
        recentProjects: ['客服流程優化', '用戶滿意度提升', '營運效率改善'],
        teamPerformance: '客戶滿意度92%，響應時間持續縮短',
        collaborationEfficiency: '內部協作順暢，外部溝通積極'
      }
    ];
  }
}

module.exports = DataService;