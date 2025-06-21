# 🧪 測試驅動開發框架 (TDD)
## HR AI 人才生態系統平台

### 📝 文檔資訊
- **版本**: v1.0
- **建立日期**: 2025-06-21
- **最後更新**: 2025-06-21
- **負責人**: QA 團隊
- **狀態**: 實施中

---

## 🎯 TDD 概述

### 測試驅動開發原則
測試驅動開發 (Test-Driven Development) 是一種軟體開發方法論，遵循 **Red-Green-Refactor** 循環：

1. **🔴 Red**: 編寫失敗的測試
2. **🟢 Green**: 編寫最少代碼使測試通過
3. **🔵 Refactor**: 重構代碼提升品質

### TDD 在 HR AI 平台的價值
- **質量保證**: 確保每個功能都有對應測試
- **回歸防護**: 預防新功能破壞現有功能
- **文檔化**: 測試即文檔，清楚描述功能行為
- **重構信心**: 安全地改進代碼結構
- **AI 可靠性**: 確保 AI 分析結果的一致性和準確性

---

## 🏗️ 測試架構設計

### 測試金字塔結構

```
         /\
        /  \
       / E2E \     < 10% - 端到端測試
      /______\
     /        \
    /Integration\ < 20% - 整合測試  
   /____________\
  /              \
 /   Unit Tests   \ < 70% - 單元測試
/__________________\
```

#### 1. 單元測試 (70%)
- **目的**: 測試個別函數和組件
- **範圍**: 純函數、組件邏輯、工具函數
- **工具**: Jest, Vue Test Utils
- **執行頻率**: 每次代碼提交

#### 2. 整合測試 (20%)
- **目的**: 測試組件間互動和 API 整合
- **範圍**: API 調用、數據流、LLM 整合
- **工具**: Jest, Supertest, Mock Service Worker
- **執行頻率**: 每次構建

#### 3. 端到端測試 (10%)
- **目的**: 測試完整用戶流程
- **範圍**: 關鍵用戶路徑、跨瀏覽器兼容性
- **工具**: Playwright, Cypress
- **執行頻率**: 每次發布前

---

## 🔧 技術工具配置

### 前端測試工具配置

#### Jest + Vue Test Utils 配置
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest'
  },
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  collectCoverageFrom: [
    'src/**/*.{js,vue}',
    '!src/main.js',
    '!src/router/index.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

#### Vitest 配置 (推薦用於 Vue 3)
```javascript
// vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    coverage: {
      reporter: ['text', 'json', 'html'],
      threshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  }
})
```

### 後端測試工具配置

#### Node.js + Supertest 配置
```javascript
// tests/setup.js
const { beforeAll, afterAll } = require('@jest/globals');
const testDb = require('./testDatabase');

beforeAll(async () => {
  await testDb.connect();
  await testDb.seed();
});

afterAll(async () => {
  await testDb.cleanup();
  await testDb.disconnect();
});
```

---

## 📋 測試用例設計

### 1. LLM 整合測試

#### LLM 客戶端測試
```javascript
// tests/unit/llm/HighQualityLLMClient.test.js
import { describe, it, expect, vi } from 'vitest'
import { HighQualityLLMClient, LLMConfig, LLMProvider } from '@/lib/llm'

describe('HighQualityLLMClient', () => {
  describe('OpenAI Provider', () => {
    it('should initialize OpenAI client successfully', () => {
      const config = new LLMConfig({
        provider: LLMProvider.OPENAI,
        model_name: 'gpt-4',
        api_key: 'test-key'
      })
      
      const client = new HighQualityLLMClient(config)
      expect(client.client).toBeDefined()
    })

    it('should generate response for employee analysis', async () => {
      const config = new LLMConfig({
        provider: LLMProvider.OPENAI,
        model_name: 'gpt-4',
        api_key: 'test-key'
      })
      
      const client = new HighQualityLLMClient(config)
      
      // Mock OpenAI response
      const mockResponse = {
        choices: [{
          message: {
            content: '這是一個測試回應，包含專業的HR分析建議。'
          }
        }]
      }
      
      vi.spyOn(client.client.chat.completions, 'create')
        .mockResolvedValue(mockResponse)
      
      const result = await client.generate(
        '請分析員工資料',
        '你是HR專家'
      )
      
      expect(result).toContain('專業的HR分析')
      expect(client.client.chat.completions.create).toHaveBeenCalledWith({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: '你是HR專家' },
          { role: 'user', content: '請分析員工資料' }
        ],
        temperature: 0.7,
        max_tokens: 2000
      })
    })

    it('should fallback when API fails', async () => {
      const config = new LLMConfig({
        provider: LLMProvider.OPENAI,
        model_name: 'gpt-4',
        api_key: 'invalid-key'
      })
      
      const client = new HighQualityLLMClient(config)
      
      // Mock API failure
      vi.spyOn(client.client.chat.completions, 'create')
        .mockRejectedValue(new Error('API Error'))
      
      const result = await client.generate('測試提示')
      
      expect(result).toContain('系統備用回應')
      expect(result).toContain('建議配置適當的LLM')
    })
  })

  describe('Ollama Provider', () => {
    it('should connect to local Ollama server', async () => {
      const config = new LLMConfig({
        provider: LLMProvider.OLLAMA,
        model_name: 'llama2:13b',
        base_url: 'http://localhost:11434'
      })
      
      // Mock successful Ollama connection
      global.fetch = vi.fn(() =>
        Promise.resolve({
          status: 200,
          json: () => Promise.resolve({ models: [] })
        })
      )
      
      const client = new HighQualityLLMClient(config)
      expect(client.client).toBe('ollama')
    })
  })
})
```

#### 品質評估測試
```javascript
// tests/unit/llm/QualityAssessment.test.js
import { describe, it, expect } from 'vitest'
import { QualityAssessment } from '@/lib/llm'

describe('QualityAssessment', () => {
  describe('assess_response_quality', () => {
    it('should give high score for quality response', () => {
      const response = `
        **員工分析報告**
        
        基於提供的資料，以下是詳細的分析和建議：
        
        ## 核心優勢
        - 技術能力突出
        - 溝通協作能力良好
        - 學習適應能力強
        
        ## 發展建議
        1. 建議加強領導力培養
        2. 可參與跨部門專案
        3. 建議申請技術培訓課程
        
        ## 職業規劃
        短期目標：高級工程師
        中期目標：技術主管
        長期目標：技術總監
      `
      
      const assessment = QualityAssessment.assess_response_quality(response)
      
      expect(assessment.quality_score).toBeGreaterThan(0.8)
      expect(assessment.is_acceptable).toBe(true)
      expect(assessment.feedback).toHaveLength(0)
    })

    it('should give low score for poor response', () => {
      const response = '好的。'
      
      const assessment = QualityAssessment.assess_response_quality(response)
      
      expect(assessment.quality_score).toBeLessThan(0.4)
      expect(assessment.is_acceptable).toBe(false)
      expect(assessment.feedback.length).toBeGreaterThan(0)
    })

    it('should detect missing HR terminology', () => {
      const response = `
        This is a basic analysis without professional HR terms.
        The person seems good at their job.
        They should probably get promoted.
      `
      
      const assessment = QualityAssessment.assess_response_quality(response)
      
      expect(assessment.feedback).toContain('建議使用更多HR專業術語')
    })
  })
})
```

### 2. Vue 組件測試

#### 認知按鈕組件測試
```javascript
// tests/unit/components/CognitiveButton.test.js
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CognitiveButton from '@/components/CognitiveButton.vue'

describe('CognitiveButton', () => {
  it('renders with correct text', () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: '開始分析'
      }
    })
    
    expect(wrapper.text()).toContain('開始分析')
  })

  it('applies correct variant styles', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        variant: 'primary'
      },
      slots: {
        default: '主要按鈕'
      }
    })
    
    const button = wrapper.find('button')
    expect(button.element.style.backgroundColor).toBe('rgb(37, 99, 235)')
  })

  it('shows loading state correctly', async () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        isLoading: true
      },
      slots: {
        default: '載入中'
      }
    })
    
    expect(wrapper.find('.loading-spinner')).toBeTruthy()
    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: '點擊我'
      }
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not emit click when disabled', async () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        disabled: true
      },
      slots: {
        default: '禁用按鈕'
      }
    })
    
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('click')).toBeUndefined()
  })
})
```

#### 員工分析表單測試
```javascript
// tests/unit/components/EmployeeAnalysisForm.test.js
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import EmployeeAnalysisForm from '@/components/EmployeeAnalysisForm.vue'

describe('EmployeeAnalysisForm', () => {
  it('validates required fields', async () => {
    const wrapper = mount(EmployeeAnalysisForm)
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.find('[data-testid="name-error"]').text())
      .toContain('員工姓名為必填項目')
  })

  it('collects form data correctly', async () => {
    const wrapper = mount(EmployeeAnalysisForm)
    
    await wrapper.find('[data-testid="employee-name"]').setValue('王小明')
    await wrapper.find('[data-testid="department"]').setValue('engineering')
    await wrapper.find('[data-testid="role"]').setValue('軟體工程師')
    await wrapper.find('[data-testid="experience"]').setValue('3')
    await wrapper.find('[data-testid="performance"]').setValue('0.85')
    
    const form = wrapper.find('form')
    await form.trigger('submit')
    
    expect(wrapper.emitted('submit')[0][0]).toEqual({
      name: '王小明',
      department: 'engineering',
      role: '軟體工程師',
      experience_years: 3,
      performance_score: 0.85,
      skills: {},
      career_goals: [],
      interests: []
    })
  })

  it('handles skill addition dynamically', async () => {
    const wrapper = mount(EmployeeAnalysisForm)
    
    // 添加技能
    await wrapper.find('[data-testid="add-skill"]').trigger('click')
    
    const skillInputs = wrapper.findAll('[data-testid^="skill-name"]')
    expect(skillInputs).toHaveLength(2) // 預設1個 + 新增1個
    
    // 填寫技能資料
    await skillInputs[0].setValue('Python')
    await wrapper.findAll('[data-testid^="skill-score"]')[0].setValue('0.8')
    
    await wrapper.find('form').trigger('submit')
    
    const formData = wrapper.emitted('submit')[0][0]
    expect(formData.skills).toEqual({ 'Python': 0.8 })
  })
})
```

### 3. API 整合測試

#### 員工分析 API 測試
```javascript
// tests/integration/api/employeeAnalysis.test.js
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import request from 'supertest'
import app from '@/server/app'
import testDb from '../helpers/testDatabase'

describe('/api/employee-analysis', () => {
  beforeAll(async () => {
    await testDb.setup()
  })

  afterAll(async () => {
    await testDb.cleanup()
  })

  describe('POST /api/employee-analysis', () => {
    it('should analyze employee successfully', async () => {
      const employeeData = {
        name: '測試員工',
        department: 'engineering',
        role: '軟體工程師',
        experience_years: 3,
        performance_score: 0.85,
        skills: {
          'Python': 0.8,
          '溝通能力': 0.7
        },
        career_goals: ['技術專家', '團隊領導'],
        interests: ['人工智能', '專案管理']
      }

      const response = await request(app)
        .post('/api/employee-analysis')
        .send(employeeData)
        .expect(200)

      expect(response.body).toHaveProperty('employee_id')
      expect(response.body).toHaveProperty('detailed_analysis')
      expect(response.body).toHaveProperty('quality_assessment')
      expect(response.body.quality_assessment.is_acceptable).toBe(true)
    })

    it('should validate input data', async () => {
      const invalidData = {
        name: '', // 空名稱
        department: 'invalid_dept'
      }

      const response = await request(app)
        .post('/api/employee-analysis')
        .send(invalidData)
        .expect(400)

      expect(response.body.error).toContain('驗證失敗')
    })

    it('should handle LLM service failure gracefully', async () => {
      // Mock LLM service failure
      vi.mock('@/services/llmService', () => ({
        analyzeEmployee: vi.fn().mockRejectedValue(new Error('LLM 服務暫時不可用'))
      }))

      const employeeData = {
        name: '測試員工',
        department: 'engineering'
      }

      const response = await request(app)
        .post('/api/employee-analysis')
        .send(employeeData)
        .expect(200)

      expect(response.body.detailed_analysis).toContain('系統備用回應')
    })
  })
})
```

### 4. 端到端測試

#### 完整用戶流程測試
```javascript
// tests/e2e/employeeAnalysisFlow.spec.js
import { test, expect } from '@playwright/test'

test.describe('Employee Analysis Flow', () => {
  test('complete employee analysis workflow', async ({ page }) => {
    // 1. 導航到主頁
    await page.goto('/')
    
    // 2. 點擊員工分析
    await page.click('[data-testid="employee-analysis-nav"]')
    
    // 3. 驗證頁面載入
    await expect(page.locator('h1')).toContainText('員工分析')
    
    // 4. 填寫員工基本資料
    await page.fill('[data-testid="employee-name"]', '王小明')
    await page.selectOption('[data-testid="department"]', 'engineering')
    await page.fill('[data-testid="role"]', '資深軟體工程師')
    await page.fill('[data-testid="experience"]', '5')
    await page.fill('[data-testid="performance"]', '0.85')
    
    // 5. 添加技能資料
    await page.fill('[data-testid="skill-name-0"]', 'Python')
    await page.fill('[data-testid="skill-score-0"]', '0.8')
    
    await page.click('[data-testid="add-skill"]')
    await page.fill('[data-testid="skill-name-1"]', '溝通能力')
    await page.fill('[data-testid="skill-score-1"]', '0.7')
    
    // 6. 填寫職業目標
    await page.fill('[data-testid="career-goals"]', 
      '成為技術專家，承擔更多領導責任')
    await page.fill('[data-testid="interests"]', 
      '人工智能，團隊管理，產品開發')
    
    // 7. 提交分析
    await page.click('[data-testid="submit-analysis"]')
    
    // 8. 驗證載入狀態
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible()
    await expect(page.locator('text=AI 正在分析中')).toBeVisible()
    
    // 9. 等待分析完成
    await page.waitForSelector('[data-testid="analysis-results"]', { 
      timeout: 30000 
    })
    
    // 10. 驗證結果顯示
    await expect(page.locator('[data-testid="analysis-results"]')).toBeVisible()
    await expect(page.locator('text=分析結果')).toBeVisible()
    await expect(page.locator('text=信心度:')).toBeVisible()
    
    // 11. 驗證結果內容
    const analysisContent = page.locator('[data-testid="analysis-content"]')
    await expect(analysisContent).toContainText('王小明')
    await expect(analysisContent).toContainText('技術能力')
    await expect(analysisContent).toContainText('發展建議')
    
    // 12. 測試報告下載
    const downloadPromise = page.waitForEvent('download')
    await page.click('[data-testid="download-report"]')
    const download = await downloadPromise
    expect(download.suggestedFilename()).toMatch(/.*\.pdf$/)
  })

  test('form validation prevents invalid submission', async ({ page }) => {
    await page.goto('/employee-analysis')
    
    // 嘗試提交空表單
    await page.click('[data-testid="submit-analysis"]')
    
    // 驗證錯誤訊息顯示
    await expect(page.locator('[data-testid="name-error"]'))
      .toContainText('員工姓名為必填項目')
    
    // 驗證表單未提交
    await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible()
  })

  test('handles network errors gracefully', async ({ page }) => {
    // 模擬網路錯誤
    await page.route('/api/employee-analysis', route => 
      route.fulfill({ status: 500, body: 'Server Error' })
    )
    
    await page.goto('/employee-analysis')
    
    // 填寫基本資料
    await page.fill('[data-testid="employee-name"]', '測試員工')
    await page.click('[data-testid="submit-analysis"]')
    
    // 驗證錯誤處理
    await expect(page.locator('[data-testid="error-message"]'))
      .toContainText('分析過程中發生錯誤')
  })
})
```

---

## 📊 測試覆蓋率要求

### 覆蓋率目標

| 類型 | 最低要求 | 目標 | 關鍵模組要求 |
|------|----------|------|-------------|
| **行覆蓋率** | 80% | 90% | 95% (LLM, 品質評估) |
| **分支覆蓋率** | 75% | 85% | 90% (錯誤處理) |
| **函數覆蓋率** | 85% | 95% | 100% (公共 API) |
| **語句覆蓋率** | 80% | 90% | 95% (核心邏輯) |

### 關鍵模組特別要求

#### LLM 整合模組
- **覆蓋率**: 95%
- **重點**: 所有 LLM 提供商的成功和失敗情況
- **特殊測試**: API 限流、超時、備用方案

#### 認知 UI 組件
- **覆蓋率**: 90%
- **重點**: 用戶互動、狀態變化、無障礙功能
- **特殊測試**: 鍵盤導航、螢幕閱讀器支援

#### 品質評估系統
- **覆蓋率**: 95%
- **重點**: 各種品質指標、邊界條件
- **特殊測試**: 極端情況、多語言內容

---

## 🔄 CI/CD 整合

### GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run unit tests
        run: npm run test:unit
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Setup test database
        run: npm run db:test:setup
      
      - name: Run integration tests
        run: npm run test:integration

  e2e-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Install Playwright
        run: npx playwright install
      
      - name: Run E2E tests
        run: npm run test:e2e
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

### 測試腳本配置

```json
{
  "scripts": {
    "test": "npm run test:unit && npm run test:integration",
    "test:unit": "vitest run --coverage",
    "test:unit:watch": "vitest",
    "test:integration": "jest tests/integration --detectOpenHandles",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:coverage": "vitest run --coverage && open coverage/index.html",
    "test:ci": "npm run test:unit && npm run test:integration && npm run test:e2e"
  }
}
```

---

## 📈 測試指標和監控

### 測試品質指標

#### 自動化指標
- **測試執行時間**: < 5 分鐘 (單元測試)
- **測試穩定性**: 成功率 > 98%
- **測試維護成本**: 每個功能變更影響測試數 < 3
- **缺陷檢出率**: 測試階段檢出率 > 85%

#### 手動監控指標
- **測試案例更新頻率**: 每月檢查
- **測試覆蓋率趨勢**: 持續監控
- **測試執行報告**: 每週分析
- **缺陷追蹤**: 實時監控

### 品質閘門

#### 程式碼品質要求
```javascript
// 必須通過的品質檢查
module.exports = {
  qualityGates: {
    coverage: {
      lines: 80,
      functions: 85,
      branches: 75,
      statements: 80
    },
    complexity: {
      maxCyclomaticComplexity: 10,
      maxCognitiveComplexity: 15
    },
    maintainability: {
      minMaintainabilityIndex: 70
    },
    security: {
      noHighVulnerabilities: true,
      noMediumVulnerabilities: true
    }
  }
}
```

---

## 🎯 最佳實踐和規範

### 測試命名規範

#### 測試檔案命名
```
src/
├── components/
│   ├── CognitiveButton.vue
│   └── __tests__/
│       └── CognitiveButton.test.js
├── services/
│   ├── llmService.js
│   └── __tests__/
│       └── llmService.test.js
└── utils/
    ├── helpers.js
    └── __tests__/
        └── helpers.test.js
```

#### 測試函數命名
```javascript
describe('Component/Function Name', () => {
  describe('when condition', () => {
    it('should expected behavior', () => {
      // 測試實現
    })
  })
})

// 範例：
describe('CognitiveButton', () => {
  describe('when variant is primary', () => {
    it('should apply primary color styles', () => {
      // 測試主要按鈕樣式
    })
  })
  
  describe('when loading is true', () => {
    it('should show spinner and disable button', () => {
      // 測試載入狀態
    })
  })
})
```

### 測試資料管理

#### 測試資料工廠
```javascript
// tests/factories/employeeFactory.js
import { faker } from '@faker-js/faker/locale/zh_TW'

export const createEmployee = (overrides = {}) => ({
  id: faker.string.uuid(),
  name: faker.person.fullName(),
  department: faker.helpers.arrayElement([
    'engineering', 'marketing', 'sales', 'hr', 'finance'
  ]),
  role: faker.person.jobTitle(),
  experience_years: faker.number.int({ min: 0, max: 20 }),
  performance_score: faker.number.float({ min: 0, max: 1, precision: 0.01 }),
  skills: {
    [faker.person.jobArea()]: faker.number.float({ min: 0.1, max: 1.0, precision: 0.1 }),
    '溝通能力': faker.number.float({ min: 0.1, max: 1.0, precision: 0.1 }),
    '團隊協作': faker.number.float({ min: 0.1, max: 1.0, precision: 0.1 })
  },
  career_goals: [
    faker.person.jobTitle(),
    faker.person.jobArea()
  ],
  interests: [
    faker.person.jobArea(),
    faker.company.buzzNoun()
  ],
  ...overrides
})

export const createTeam = (size = 5, overrides = {}) => ({
  id: faker.string.uuid(),
  name: `${faker.company.buzzAdjective()}團隊`,
  department: faker.commerce.department(),
  members: Array.from({ length: size }, () => createEmployee()),
  avg_performance: faker.number.float({ min: 0.6, max: 0.95, precision: 0.01 }),
  ...overrides
})
```

### Mock 策略

#### LLM 服務 Mock
```javascript
// tests/mocks/llmService.js
export const mockLLMService = {
  analyzeEmployee: vi.fn().mockImplementation((employeeData) => {
    return Promise.resolve({
      employee_id: employeeData.id || 'test-id',
      employee_name: employeeData.name || '測試員工',
      analysis_timestamp: new Date().toISOString(),
      detailed_analysis: `基於${employeeData.name}的資料分析，該員工展現出優秀的潛力...`,
      quality_assessment: {
        quality_score: 0.85,
        max_score: 1.0,
        feedback: [],
        is_acceptable: true
      },
      llm_provider: 'openai',
      model_used: 'gpt-4'
    })
  })
}
```

#### API Mock (MSW)
```javascript
// tests/mocks/handlers.js
import { rest } from 'msw'

export const handlers = [
  rest.post('/api/employee-analysis', (req, res, ctx) => {
    const { name } = req.body
    
    return res(
      ctx.status(200),
      ctx.json({
        employee_id: 'test-id',
        employee_name: name,
        detailed_analysis: '這是模擬的分析結果...',
        quality_assessment: {
          quality_score: 0.85,
          is_acceptable: true
        }
      })
    )
  }),

  rest.get('/api/analysis-history', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          employee_name: '王小明',
          timestamp: '2025-06-21T10:00:00Z',
          quality_score: 0.87
        }
      ])
    )
  })
]
```

---

## 📚 測試文檔和維護

### 測試計劃文檔
每個功能模組應包含：
1. **測試範圍**: 明確測試邊界
2. **測試策略**: 選擇適當的測試方法
3. **測試資料**: 定義測試用的資料集
4. **預期結果**: 清楚描述期望行為
5. **維護計劃**: 測試更新和維護策略

### 持續改進
- **每週測試回顧**: 分析測試結果和改進機會
- **月度測試審查**: 評估測試覆蓋率和品質
- **季度測試策略檢討**: 調整測試方法和工具
- **年度測試架構升級**: 引入新的測試技術和最佳實踐

---

此 TDD 框架為 HR AI 平台提供了完整的測試策略和實施指南，確保開發品質和產品可靠性。