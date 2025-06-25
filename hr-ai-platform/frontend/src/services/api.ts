/**
 * API 服務層
 * 提供與後端API的通信接口
 */

import axios, { AxiosInstance, AxiosError } from 'axios'

// API 響應接口
interface APIResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  total?: number
}

// 員工分析請求參數
interface EmployeeAnalysisRequest {
  analysisType?: 'comprehensive' | 'performance' | 'skills' | 'potential'
  timeRange?: '3months' | '6months' | '1year' | 'all'
  recentPerformance?: string
  feedback?: string
  projectContribution?: string
}

// 團隊分析請求參數
interface TeamAnalysisRequest {
  analysisDepth?: 'basic' | 'standard' | 'comprehensive'
  analysisPeriod?: '1month' | '3months' | '6months' | '1year'
  collaborationMode?: string
  teamPerformance?: string
  collaborationEfficiency?: string
}

class APIService {
  private client: AxiosInstance
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 60000, // 60秒超時 (AI分析可能需要較長時間)
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 請求攔截器
    this.client.interceptors.request.use(
      (config) => {
        // 添加請求ID用於追蹤
        config.headers['x-request-id'] = this.generateRequestId()
        
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        if (config.data) {
          console.log('📤 Request Data:', config.data)
        }
        
        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )

    // 響應攔截器
    this.client.interceptors.response.use(
      (response) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        console.log('📥 Response Data:', response.data)
        return response
      },
      (error: AxiosError) => {
        console.error(`❌ API Error: ${error.message}`)
        
        if (error.response) {
          console.error('📥 Error Response:', error.response.data)
          console.error('📊 Status:', error.response.status)
        } else if (error.request) {
          console.error('📡 No Response:', error.request)
        }
        
        return Promise.reject(this.formatError(error))
      }
    )
  }

  private generateRequestId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  private formatError(error: AxiosError): Error {
    if (error.response?.data) {
      const errorData = error.response.data as any
      return new Error(errorData.error || errorData.message || 'API request failed')
    } else if (error.request) {
      return new Error('網路連接失敗，請檢查後端服務是否正常運行')
    } else {
      return new Error(error.message || 'Unknown error occurred')
    }
  }

  // 健康檢查
  async healthCheck(): Promise<APIResponse> {
    const response = await this.client.get('/health')
    return response.data
  }

  async detailedHealthCheck(): Promise<APIResponse> {
    const response = await this.client.get('/health/detailed')
    return response.data
  }

  // 員工相關 API
  async getEmployees(): Promise<APIResponse> {
    const response = await this.client.get('/api/employees')
    return response.data
  }

  async getEmployee(id: string): Promise<APIResponse> {
    const response = await this.client.get(`/api/employees/${id}`)
    return response.data
  }

  async analyzeEmployee(
    employeeId: string, 
    params: EmployeeAnalysisRequest = {}
  ): Promise<APIResponse> {
    const response = await this.client.post(`/api/employees/${employeeId}/analyze`, params)
    return response.data
  }

  async getEmployeeHistory(employeeId: string, limit = 10): Promise<APIResponse> {
    const response = await this.client.get(`/api/employees/${employeeId}/history`, {
      params: { limit }
    })
    return response.data
  }

  async addEmployee(employeeData: any): Promise<APIResponse> {
    const response = await this.client.post('/api/employees', employeeData)
    return response.data
  }

  async updateEmployee(id: string, updates: any): Promise<APIResponse> {
    const response = await this.client.put(`/api/employees/${id}`, updates)
    return response.data
  }

  async batchAnalyzeEmployees(
    employeeIds: string[], 
    params: EmployeeAnalysisRequest = {}
  ): Promise<APIResponse> {
    const response = await this.client.post('/api/employees/batch-analyze', {
      employeeIds,
      ...params
    })
    return response.data
  }

  // 團隊相關 API
  async getTeams(): Promise<APIResponse> {
    const response = await this.client.get('/api/teams')
    return response.data
  }

  async getTeam(id: string): Promise<APIResponse> {
    const response = await this.client.get(`/api/teams/${id}`)
    return response.data
  }

  async analyzeTeam(
    teamId: string, 
    params: TeamAnalysisRequest = {}
  ): Promise<APIResponse> {
    const response = await this.client.post(`/api/teams/${teamId}/analyze`, params)
    return response.data
  }

  async getTeamHistory(teamId: string, limit = 10): Promise<APIResponse> {
    const response = await this.client.get(`/api/teams/${teamId}/history`, {
      params: { limit }
    })
    return response.data
  }

  async getTeamMembersOverview(teamId: string): Promise<APIResponse> {
    const response = await this.client.get(`/api/teams/${teamId}/members-overview`)
    return response.data
  }

  async compareTeams(teamIds: string[]): Promise<APIResponse> {
    const response = await this.client.post('/api/teams/compare', { teamIds })
    return response.data
  }

  // RAG智能查詢
  async query(question: string): Promise<APIResponse> {
    const response = await this.client.post('/api/rag/query', { question })
    return response.data
  }

  async analyzeQuery(question: string): Promise<APIResponse> {
    const response = await this.client.post('/api/rag/analyze', { question })
    return response.data
  }

  // 文件上傳
  async uploadDocument(file: File): Promise<APIResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await this.client.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }

  async getRecentDocuments(limit = 10): Promise<APIResponse> {
    const response = await this.client.get('/api/documents/recent', {
      params: { limit }
    })
    return response.data
  }

  // 聊天會話管理
  async getChatSessions(): Promise<APIResponse> {
    const response = await this.client.get('/api/chat/sessions')
    return response.data
  }

  async createChatSession(title?: string): Promise<APIResponse> {
    const response = await this.client.post('/api/chat/sessions', { title })
    return response.data
  }

  async getChatMessages(sessionId: string): Promise<APIResponse> {
    const response = await this.client.get(`/api/chat/sessions/${sessionId}/messages`)
    return response.data
  }

  // 系統狀態
  async getSystemStatus(): Promise<APIResponse> {
    const response = await this.client.get('/api/system/status')
    return response.data
  }

  async getLLMStatus(): Promise<APIResponse> {
    const response = await this.client.get('/api/system/llm-status')
    return response.data
  }

  // 工具方法
  isOnline(): boolean {
    return navigator.onLine
  }

  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck()
      return true
    } catch (error) {
      console.warn('🔌 後端連接測試失敗:', error)
      return false
    }
  }

  getBaseURL(): string {
    return this.baseURL
  }

  // 錯誤處理工具
  handleAPIError(error: any): string {
    if (error.message) {
      return error.message
    } else if (typeof error === 'string') {
      return error
    } else {
      return '發生未知錯誤，請稍後重試'
    }
  }
}

// 創建單例實例
export const apiService = new APIService()

// 導出類型定義
export type { 
  APIResponse, 
  EmployeeAnalysisRequest, 
  TeamAnalysisRequest 
}

export default apiService