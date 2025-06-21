# 🎭 行為驅動開發框架 (BDD)
## HR AI 人才生態系統平台

### 📝 文檔資訊
- **版本**: v1.0
- **建立日期**: 2025-06-21
- **最後更新**: 2025-06-21
- **負責人**: 產品 + 開發團隊
- **狀態**: 實施中

---

## 🎯 BDD 概述

### 行為驅動開發原則
行為驅動開發 (Behavior-Driven Development) 是一種敏捷軟體開發方法，強調：

1. **🤝 協作溝通**: 業務、開發、測試團隊共同定義需求
2. **📝 共同語言**: 使用自然語言描述系統行為
3. **🎯 用戶價值**: 關注用戶需求和業務價值
4. **✅ 可執行規格**: 規格即測試，測試即文檔

### BDD 在 HR AI 平台的價值
- **需求澄清**: 確保所有人對功能需求的理解一致
- **用戶中心**: 從用戶角度定義系統行為
- **活文檔**: 規格書同時是測試和文檔
- **迴歸保護**: 防止需求變更時功能退化
- **溝通橋樑**: 技術團隊與業務團隊的溝通媒介

---

## 🏗️ BDD 架構設計

### Gherkin 語法結構

```gherkin
Feature: 功能名稱
  As a [角色]
  I want [功能]
  So that [價值]

  Background:
    Given [前置條件]

  Scenario: 場景名稱
    Given [前置條件]
    When [動作]
    Then [預期結果]
    And [附加條件]
    But [例外情況]

  Scenario Outline: 場景大綱
    Given [參數化前置條件]
    When [參數化動作]
    Then [參數化結果]
    
    Examples:
      | 參數1 | 參數2 | 結果 |
      | 值1   | 值2   | 值3  |
```

### 技術工具棧

#### 前端 BDD 工具
```javascript
// Cucumber.js + Jest
主要工具: @cucumber/cucumber
測試框架: Jest
斷言庫: expect (Jest內建)
頁面操作: @testing-library/vue
API Mock: Mock Service Worker (MSW)
```

#### 端到端 BDD 工具
```javascript
// Playwright + Cucumber
主要工具: @cucumber/cucumber
瀏覽器控制: Playwright
報告工具: @cucumber/html-formatter
CI整合: GitHub Actions
```

---

## 📋 功能規格設計

### 1. 員工分析功能

#### Feature: 員工個人分析
```gherkin
Feature: 員工個人分析
  As a HR 專員
  I want to 分析員工的能力和發展潛力
  So that 我可以提供客觀的職業發展建議

  Background:
    Given 我已登入 HR AI 系統
    And 我在員工分析頁面

  Scenario: 成功分析優秀員工
    Given 我有一位表現優秀的員工資料
    When 我輸入員工基本資訊：
      | 欄位     | 值         |
      | 姓名     | 王小明     |
      | 部門     | 軟體工程部 |
      | 職位     | 資深工程師 |
      | 年資     | 5          |
      | 績效分數 | 0.9        |
    And 我添加技能評估：
      | 技能     | 分數 |
      | Python   | 0.9  |
      | 領導力   | 0.7  |
      | 溝通能力 | 0.8  |
    And 我設定職業目標為 "成為技術主管"
    And 我點擊 "開始 AI 分析"
    Then 我應該看到載入指示器
    And 系統應該在 30 秒內完成分析
    And 我應該看到分析結果包含：
      | 區塊       | 內容                   |
      | 優勢分析   | 技術能力突出           |
      | 發展建議   | 建議加強領導力培養     |
      | 職業路徑   | 短期：高級工程師       |
      | 行動計劃   | 參加管理培訓課程       |
    And 分析信心度應該大於 80%

  Scenario: 處理員工資料不完整的情況
    Given 我要分析一位資料不完整的員工
    When 我只輸入員工姓名 "李小華"
    And 我點擊 "開始 AI 分析"
    Then 我應該看到警告訊息 "資料不完整，分析結果可能不夠準確"
    And 系統仍應該產生基礎分析報告
    And 報告應該標註 "建議補充更多資訊以提升分析準確度"

  Scenario: 偏見檢測機制
    Given 我輸入員工資料包含可能引起偏見的資訊
    When 分析結果包含性別或年齡相關的描述
    Then 系統應該自動檢測並標記潛在偏見
    And 顯示警告訊息 "檢測到可能的評估偏見，請重新檢視分析結果"
    And 提供修正建議

  Scenario Outline: 不同經驗年資的分析差異
    Given 我輸入員工資料，年資為 <年資>
    When 我完成分析
    Then 職業發展建議應該符合 <經驗層級> 的特點
    And 培訓建議應該包含 <培訓重點>

    Examples:
      | 年資 | 經驗層級 | 培訓重點       |
      | 1    | 新人     | 基礎技能培養   |
      | 5    | 中階     | 專業深化       |
      | 10   | 資深     | 領導力發展     |
      | 15   | 專家     | 策略思維培養   |
```

#### Feature: 分析品質保證
```gherkin
Feature: 分析品質保證
  As a HR 主管
  I want to 確保每次分析都達到品質標準
  So that 我可以信任分析結果來做重要決策

  Background:
    Given AI 分析系統已啟動
    And 品質評估機制已就緒

  Scenario: 高品質分析通過驗證
    Given 我提交一份完整的員工資料
    When AI 完成分析
    Then 品質評估分數應該大於 0.8
    And 分析結果應該包含：
      | 必要元素     | 檢查點             |
      | 結構化內容   | 包含標題和段落     |
      | 專業術語     | 使用HR專業詞彙     |
      | 具體建議     | 可執行的行動方案   |
      | 客觀性       | 避免主觀判斷用詞   |
    And 系統標記為 "分析品質：優良"

  Scenario: 低品質分析觸發改善機制
    Given AI 生成的初次分析品質較低
    When 品質評估分數小於 0.6
    Then 系統應該自動觸發品質改善流程
    And 重新生成更詳細的分析
    And 如果改善後仍不達標，應該使用備用回應模板
    And 記錄品質問題供後續改進

  Scenario: 多模型對比驗證
    Given 設定使用多個 LLM 模型進行分析
    When 對同一員工進行分析
    Then 系統應該比較不同模型的結果
    And 選擇品質最高的分析結果
    And 如果結果差異過大，應該標記需要人工審查
```

### 2. 團隊分析功能

#### Feature: 團隊動態分析
```gherkin
Feature: 團隊動態分析
  As a 部門主管
  I want to 了解團隊的整體能力和協作狀況
  So that 我可以優化團隊配置和提升團隊效能

  Background:
    Given 我已登入系統並有團隊管理權限
    And 我在團隊分析頁面

  Scenario: 分析高績效團隊
    Given 我有一個高績效的開發團隊：
      | 成員   | 職位       | 年資 | 主要技能   | 績效 |
      | 張三   | 技術主管   | 8    | 架構設計   | 0.95 |
      | 李四   | 資深工程師 | 6    | 前端開發   | 0.88 |
      | 王五   | 工程師     | 3    | 後端開發   | 0.82 |
      | 趙六   | 工程師     | 2    | 測試自動化 | 0.85 |
    When 我提交團隊分析請求
    Then 我應該看到團隊優勢分析：
      | 分析維度   | 結果                       |
      | 技能互補性 | 高度互補，涵蓋全棧開發     |
      | 經驗分布   | 合理的資深-中階-新人配置   |
      | 協作效能   | 溝通順暢，決策效率高       |
      | 發展潛力   | 具備向更高目標發展的能力   |
    And 得到改善建議：
      | 建議類型   | 具體建議                   |
      | 知識管理   | 建立技術分享機制           |
      | 人才培養   | 為新人安排導師             |
      | 流程優化   | 引入敏捷開發實踐           |

  Scenario: 識別團隊問題和風險
    Given 我有一個存在問題的團隊：
      | 問題描述     | 具體表現                   |
      | 技能缺口     | 缺乏前端開發專業人才       |
      | 經驗不足     | 大部分成員年資少於2年      |
      | 溝通問題     | 跨部門協作效率低           |
      | 績效差異     | 成員間績效差距較大         |
    When 我進行團隊分析
    Then 系統應該識別關鍵風險：
      | 風險類型     | 風險等級 | 影響描述               |
      | 技能依賴     | 高       | 關鍵技能過度集中       |
      | 人才流失     | 中       | 高績效成員離職風險     |
      | 協作效率     | 中       | 專案交付可能延遲       |
    And 提供風險緩解建議：
      | 建議         | 優先級 | 預期效果               |
      | 招聘前端工程師 | 高     | 填補關鍵技能缺口       |
      | 建立知識文檔   | 高     | 降低人員依賴           |
      | 改善溝通機制   | 中     | 提升協作效率           |

  Scenario: 團隊成長軌跡追蹤
    Given 我想了解團隊近期的發展變化
    When 我選擇查看團隊歷史分析
    Then 我應該看到團隊能力發展趨勢圖
    And 比較不同時期的團隊指標：
      | 指標       | 3個月前 | 現在  | 變化趨勢 |
      | 平均績效   | 0.75    | 0.82  | ↗ 提升   |
      | 技能廣度   | 6項     | 8項   | ↗ 擴展   |
      | 協作指數   | 0.70    | 0.85  | ↗ 改善   |
    And 識別成長驅動因素
    And 預測未來發展方向
```

### 3. 系統體驗功能

#### Feature: 認知友善介面
```gherkin
Feature: 認知友善介面
  As a HR 專業人員
  I want to 使用符合認知科學原則的介面
  So that 我可以高效且舒適地完成工作

  Background:
    Given 我打開 HR AI 分析平台
    And 介面使用認知友善設計

  Scenario: 降低認知負荷
    Given 我在員工分析表單頁面
    When 我開始填寫員工資料
    Then 每個區塊應該最多顯示 7 個主要元素
    And 相關資訊應該群組在一起
    And 重要操作應該使用主要顏色突出顯示
    And 次要資訊應該使用較淺的顏色

  Scenario: 漸進式資訊披露
    Given 我在查看分析結果頁面
    When 頁面首次載入
    Then 我應該先看到分析概覽
    And 有明確的 "查看詳細分析" 按鈕
    When 我點擊 "查看詳細分析"
    Then 系統應該展開詳細內容
    And 同時提供 "收起詳細內容" 選項
    And 保持頁面布局穩定，避免跳動

  Scenario: 注意力引導機制
    Given 我在操作複雜的分析流程
    When 每個步驟完成時
    Then 系統應該用動畫引導我注意下一步
    And 當前步驟應該用主要顏色標記
    And 已完成步驟應該用成功顏色標記
    And 未來步驟應該用中性顏色顯示

  Scenario: 即時反饋系統
    Given 我在填寫表單
    When 我輸入無效資料
    Then 應該立即顯示錯誤提示
    And 錯誤訊息應該明確說明問題
    And 提供修正建議
    When 我修正錯誤後
    Then 錯誤提示應該立即消失
    And 顯示成功確認提示

  Scenario: 無障礙功能支援
    Given 我使用鍵盤操作介面
    When 我按 Tab 鍵導航
    Then 焦點應該按邏輯順序移動
    And 當前焦點應該有清楚的視覺指示
    When 我按 Enter 鍵
    Then 應該執行當前元素的主要動作
    When 我按 Escape 鍵
    Then 應該關閉模態框或取消當前操作
```

#### Feature: 多裝置適配
```gherkin
Feature: 多裝置適配
  As a 行動辦公的 HR 人員
  I want to 在不同裝置上都能正常使用系統
  So that 我可以隨時隨地處理 HR 工作

  Scenario Outline: 響應式布局適配
    Given 我使用 <裝置類型> 訪問系統
    When 螢幕寬度為 <寬度> 像素
    Then 介面應該切換到 <布局模式>
    And 主要功能應該仍然可用
    And 文字大小應該適合 <裝置類型> 閱讀

    Examples:
      | 裝置類型 | 寬度 | 布局模式     |
      | 桌機     | 1920 | 雙欄式布局   |
      | 筆電     | 1366 | 雙欄式布局   |
      | 平板     | 768  | 單欄式布局   |
      | 手機     | 375  | 堆疊式布局   |

  Scenario: 觸控操作優化
    Given 我使用觸控裝置
    When 我點擊按鈕或連結
    Then 觸控區域應該至少 44x44 像素
    And 相鄰元素間應該有足夠間距
    And 支援滑動手勢操作
    And 避免需要精確點擊的小目標

  Scenario: 行動裝置功能限制
    Given 我使用手機訪問系統
    When 我嘗試執行複雜分析
    Then 系統應該提示建議使用大螢幕裝置
    And 仍提供基本查看功能
    And 允許查看已完成的分析報告
    And 支援基本的搜尋和篩選操作
```

### 4. 效能和可靠性

#### Feature: 系統效能
```gherkin
Feature: 系統效能
  As a 使用者
  I want to 系統回應快速且穩定
  So that 我可以高效完成工作

  Background:
    Given 系統處於正常運行狀態
    And 網路連線品質良好

  Scenario: 頁面載入效能
    Given 我訪問任何系統頁面
    When 頁面開始載入
    Then 初始內容應該在 1 秒內顯示
    And 完整頁面應該在 2 秒內載入完成
    And 重要功能應該優先載入
    And 載入過程應該有進度指示

  Scenario: AI 分析效能
    Given 我提交員工分析請求
    When 系統開始 AI 分析
    Then 應該立即顯示載入指示器
    And 提供預估完成時間
    And 單一員工分析應該在 30 秒內完成
    And 分析過程中允許取消操作
    When 分析完成時
    Then 結果應該立即顯示
    And 載入指示器應該消失

  Scenario: 大量資料處理
    Given 我上傳包含 50 位員工的批量分析檔案
    When 系統開始處理
    Then 應該顯示整體進度條
    And 提供詳細的處理狀態
    And 允許暫停和恢復處理
    And 部分完成的結果應該可以先查看
    And 整個批量分析應該在 5 分鐘內完成

  Scenario: 併發使用者處理
    Given 系統有 100 個同時線上使用者
    When 多個使用者同時提交分析請求
    Then 每個使用者的回應時間不應該明顯增加
    And 系統應該保持穩定運行
    And 重要功能應該優先保證
```

#### Feature: 錯誤處理和恢復
```gherkin
Feature: 錯誤處理和恢復
  As a 使用者
  I want to 在遇到錯誤時能夠快速恢復
  So that 我的工作不會因技術問題而中斷

  Scenario: 網路連線中斷處理
    Given 我正在填寫員工分析表單
    When 網路連線突然中斷
    Then 系統應該自動保存已填寫的資料
    And 顯示網路連線問題提示
    And 提供手動重試選項
    When 網路恢復後
    Then 自動載入之前保存的資料
    And 允許我繼續完成操作

  Scenario: LLM 服務故障處理
    Given 我提交分析請求
    When 主要 LLM 服務無法回應
    Then 系統應該自動切換到備用 LLM
    And 顯示服務切換通知
    And 分析仍能正常完成
    When 所有 LLM 都無法回應時
    Then 使用預設的分析模板
    And 明確標記這是備用回應
    And 建議稍後重試

  Scenario: 資料處理錯誤
    Given 我上傳格式有誤的員工資料檔案
    When 系統嘗試處理資料
    Then 應該清楚指出具體錯誤位置
    And 提供修正建議
    And 顯示正確的資料格式範例
    And 允許我重新上傳修正後的檔案

  Scenario: 使用者權限變更
    Given 我正在使用系統
    When 我的使用者權限被管理員變更
    Then 系統應該優雅地處理權限變化
    And 重新導向到我有權限的頁面
    And 解釋權限變更的原因
    And 提供聯絡管理員的方式
```

---

## 🔧 技術實作配置

### Cucumber.js 設定

#### 專案結構
```
features/
├── step_definitions/
│   ├── employee_analysis_steps.js
│   ├── team_analysis_steps.js
│   ├── ui_interaction_steps.js
│   └── common_steps.js
├── support/
│   ├── world.js
│   ├── hooks.js
│   └── page_objects/
│       ├── EmployeeAnalysisPage.js
│       ├── TeamAnalysisPage.js
│       └── DashboardPage.js
└── specifications/
    ├── employee_analysis.feature
    ├── team_analysis.feature
    ├── cognitive_ui.feature
    └── system_performance.feature
```

#### Cucumber 配置
```javascript
// cucumber.config.js
module.exports = {
  default: {
    formatOptions: {
      snippetInterface: 'async-await'
    },
    paths: ['features/specifications/*.feature'],
    require: ['features/step_definitions/**/*.js', 'features/support/**/*.js'],
    format: [
      'progress-bar',
      'html:reports/cucumber-report.html',
      'json:reports/cucumber-report.json'
    ],
    parallel: 2,
    retry: 1
  }
}
```

### Step Definitions 實作

#### 員工分析步驟定義
```javascript
// features/step_definitions/employee_analysis_steps.js
const { Given, When, Then } = require('@cucumber/cucumber')
const { expect } = require('@playwright/test')

Given('我已登入 HR AI 系統', async function () {
  await this.page.goto('/login')
  await this.page.fill('[data-testid="username"]', 'hr_user')
  await this.page.fill('[data-testid="password"]', 'password123')
  await this.page.click('[data-testid="login-button"]')
  await this.page.waitForURL('/dashboard')
})

Given('我在員工分析頁面', async function () {
  await this.page.goto('/employee-analysis')
  await expect(this.page.locator('h1')).toContainText('員工分析')
})

Given('我有一位表現優秀的員工資料', function () {
  this.employeeData = {
    name: '王小明',
    department: '軟體工程部',
    role: '資深工程師',
    experience: 5,
    performance: 0.9
  }
})

When('我輸入員工基本資訊：', async function (dataTable) {
  const data = dataTable.hashes()[0]
  
  await this.page.fill('[data-testid="employee-name"]', data.姓名)
  await this.page.selectOption('[data-testid="department"]', data.部門)
  await this.page.fill('[data-testid="role"]', data.職位)
  await this.page.fill('[data-testid="experience"]', data.年資)
  await this.page.fill('[data-testid="performance"]', data.績效分數)
})

When('我添加技能評估：', async function (dataTable) {
  const skills = dataTable.hashes()
  
  for (let i = 0; i < skills.length; i++) {
    if (i > 0) {
      await this.page.click('[data-testid="add-skill"]')
    }
    
    await this.page.fill(`[data-testid="skill-name-${i}"]`, skills[i].技能)
    await this.page.fill(`[data-testid="skill-score-${i}"]`, skills[i].分數)
  }
})

When('我設定職業目標為 {string}', async function (goal) {
  await this.page.fill('[data-testid="career-goals"]', goal)
})

When('我點擊 {string}', async function (buttonText) {
  await this.page.click(`text=${buttonText}`)
})

Then('我應該看到載入指示器', async function () {
  await expect(this.page.locator('[data-testid="loading-spinner"]')).toBeVisible()
})

Then('系統應該在 {int} 秒內完成分析', async function (seconds) {
  await this.page.waitForSelector('[data-testid="analysis-results"]', {
    timeout: seconds * 1000
  })
})

Then('我應該看到分析結果包含：', async function (dataTable) {
  const expectations = dataTable.hashes()
  
  for (const expectation of expectations) {
    const section = this.page.locator(`[data-testid="${expectation.區塊}"]`)
    await expect(section).toContainText(expectation.內容)
  }
})

Then('分析信心度應該大於 {int}%', async function (threshold) {
  const confidenceText = await this.page.textContent('[data-testid="confidence-score"]')
  const confidence = parseInt(confidenceText.match(/\d+/)[0])
  expect(confidence).toBeGreaterThan(threshold)
})
```

#### UI 互動步驟定義
```javascript
// features/step_definitions/ui_interaction_steps.js
const { Given, When, Then } = require('@cucumber/cucumber')
const { expect } = require('@playwright/test')

Given('我打開 HR AI 分析平台', async function () {
  await this.page.goto('/')
})

Given('介面使用認知友善設計', async function () {
  // 驗證認知設計原則的實施
  const primaryColor = await this.page.evaluate(() => {
    return getComputedStyle(document.documentElement)
      .getPropertyValue('--primary-blue')
  })
  expect(primaryColor).toBe('#2563eb')
})

Then('每個區塊應該最多顯示 {int} 個主要元素', async function (maxElements) {
  const sections = await this.page.locator('.form-section').all()
  
  for (const section of sections) {
    const mainElements = await section.locator('> *').count()
    expect(mainElements).toBeLessThanOrEqual(maxElements)
  }
})

Then('相關資訊應該群組在一起', async function () {
  // 驗證相關元素的視覺群組
  const groups = await this.page.locator('.form-group').all()
  expect(groups.length).toBeGreaterThan(0)
  
  for (const group of groups) {
    const spacing = await group.evaluate((el) => {
      return window.getComputedStyle(el).marginBottom
    })
    expect(spacing).toBeTruthy()
  }
})

When('我按 {string} 鍵導航', async function (key) {
  await this.page.keyboard.press(key)
})

Then('焦點應該按邏輯順序移動', async function () {
  const focusableElements = await this.page.locator(
    'button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ).all()
  
  let previousTabIndex = -1
  for (const element of focusableElements) {
    const tabIndex = await element.getAttribute('tabindex') || '0'
    const currentTabIndex = parseInt(tabIndex)
    expect(currentTabIndex).toBeGreaterThanOrEqual(previousTabIndex)
    previousTabIndex = currentTabIndex
  }
})
```

### Page Objects 模式

#### 員工分析頁面物件
```javascript
// features/support/page_objects/EmployeeAnalysisPage.js
class EmployeeAnalysisPage {
  constructor(page) {
    this.page = page
  }

  async navigate() {
    await this.page.goto('/employee-analysis')
    await this.page.waitForLoadState('networkidle')
  }

  async fillBasicInfo(employeeData) {
    await this.page.fill('[data-testid="employee-name"]', employeeData.name)
    
    if (employeeData.department) {
      await this.page.selectOption('[data-testid="department"]', employeeData.department)
    }
    
    if (employeeData.role) {
      await this.page.fill('[data-testid="role"]', employeeData.role)
    }
    
    if (employeeData.experience) {
      await this.page.fill('[data-testid="experience"]', employeeData.experience.toString())
    }
    
    if (employeeData.performance) {
      await this.page.fill('[data-testid="performance"]', employeeData.performance.toString())
    }
  }

  async addSkill(skillName, skillScore, index = 0) {
    if (index > 0) {
      await this.page.click('[data-testid="add-skill"]')
    }
    
    await this.page.fill(`[data-testid="skill-name-${index}"]`, skillName)
    await this.page.fill(`[data-testid="skill-score-${index}"]`, skillScore.toString())
  }

  async setCareerGoals(goals) {
    await this.page.fill('[data-testid="career-goals"]', goals)
  }

  async submitAnalysis() {
    await this.page.click('[data-testid="submit-analysis"]')
  }

  async waitForAnalysisCompletion(timeout = 30000) {
    await this.page.waitForSelector('[data-testid="analysis-results"]', { timeout })
  }

  async getAnalysisResults() {
    const results = {}
    
    // 提取分析結果的各個部分
    results.confidence = await this.page.textContent('[data-testid="confidence-score"]')
    results.summary = await this.page.textContent('[data-testid="analysis-summary"]')
    results.strengths = await this.page.textContent('[data-testid="strengths-section"]')
    results.recommendations = await this.page.textContent('[data-testid="recommendations-section"]')
    
    return results
  }

  async downloadReport() {
    const downloadPromise = this.page.waitForEvent('download')
    await this.page.click('[data-testid="download-report"]')
    return await downloadPromise
  }
}

module.exports = EmployeeAnalysisPage
```

### World 物件設定

#### 測試環境設定
```javascript
// features/support/world.js
const { setWorldConstructor, Before, After } = require('@cucumber/cucumber')
const { chromium } = require('playwright')
const EmployeeAnalysisPage = require('./page_objects/EmployeeAnalysisPage')
const TeamAnalysisPage = require('./page_objects/TeamAnalysisPage')

class CustomWorld {
  constructor() {
    this.browser = null
    this.page = null
    this.employeeAnalysisPage = null
    this.teamAnalysisPage = null
  }

  async init() {
    this.browser = await chromium.launch({ 
      headless: process.env.HEADLESS !== 'false',
      slowMo: process.env.SLOW_MO ? parseInt(process.env.SLOW_MO) : 0
    })
    
    const context = await this.browser.newContext({
      viewport: { width: 1366, height: 768 },
      locale: 'zh-TW'
    })
    
    this.page = await context.newPage()
    
    // 初始化頁面物件
    this.employeeAnalysisPage = new EmployeeAnalysisPage(this.page)
    this.teamAnalysisPage = new TeamAnalysisPage(this.page)
  }

  async cleanup() {
    if (this.browser) {
      await this.browser.close()
    }
  }
}

setWorldConstructor(CustomWorld)

Before(async function () {
  await this.init()
})

After(async function () {
  await this.cleanup()
})
```

### Hooks 和輔助功能

#### 測試鉤子設定
```javascript
// features/support/hooks.js
const { Before, After, BeforeAll, AfterAll } = require('@cucumber/cucumber')

BeforeAll(async function () {
  // 設定測試環境
  console.log('開始 BDD 測試套件')
  
  // 確保測試資料庫就緒
  if (process.env.NODE_ENV === 'test') {
    // 初始化測試資料庫
  }
})

Before({ tags: '@employee-analysis' }, async function () {
  // 為員工分析相關測試準備特定資料
  this.testEmployees = [
    {
      name: '王小明',
      department: 'engineering',
      role: '資深工程師',
      experience: 5,
      performance: 0.9
    }
  ]
})

Before({ tags: '@team-analysis' }, async function () {
  // 為團隊分析相關測試準備特定資料
  this.testTeams = [
    {
      name: '開發團隊A',
      members: this.testEmployees
    }
  ]
})

After(async function (scenario) {
  // 測試結束後清理
  if (scenario.result.status === 'FAILED') {
    // 截圖保存失敗的測試
    const screenshot = await this.page.screenshot()
    this.attach(screenshot, 'image/png')
  }
})

AfterAll(async function () {
  // 清理測試環境
  console.log('BDD 測試套件完成')
})
```

---

## 📊 BDD 報告和監控

### 測試報告配置

#### HTML 報告生成
```javascript
// scripts/generate-report.js
const reporter = require('cucumber-html-reporter')

const options = {
  theme: 'bootstrap',
  jsonFile: 'reports/cucumber-report.json',
  output: 'reports/cucumber-report.html',
  reportSuiteAsScenarios: true,
  scenarioTimestamp: true,
  launchReport: false,
  metadata: {
    "App Version": "1.0.0",
    "Test Environment": "Staging",
    "Browser": "Chrome",
    "Platform": "macOS",
    "Parallel": "Scenarios",
    "Executed": "Remote"
  }
}

reporter.generate(options)
```

### CI/CD 整合

#### GitHub Actions BDD 配置
```yaml
# .github/workflows/bdd-tests.yml
name: BDD Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  bdd-tests:
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
      
      - name: Install Playwright browsers
        run: npx playwright install
      
      - name: Run BDD tests
        run: npm run test:bdd
        env:
          HEADLESS: true
          NODE_ENV: test
      
      - name: Generate BDD report
        if: always()
        run: npm run bdd:report
      
      - name: Upload BDD report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: bdd-report
          path: reports/
      
      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs')
            const reportPath = 'reports/cucumber-report.json'
            
            if (fs.existsSync(reportPath)) {
              const report = JSON.parse(fs.readFileSync(reportPath))
              const summary = generateTestSummary(report)
              
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: summary
              })
            }
```

---

## 🎯 BDD 最佳實踐

### 場景撰寫原則

#### INVEST 原則
- **Independent**: 場景間互相獨立
- **Negotiable**: 可以討論和修改
- **Valuable**: 對業務有價值
- **Estimable**: 可以估算工作量
- **Small**: 保持適當大小
- **Testable**: 可以驗證

#### 範例改進
```gherkin
# ❌ 不好的場景
Scenario: 測試員工分析
  Given 我有員工
  When 我分析
  Then 我得到結果

# ✅ 好的場景  
Scenario: 分析高績效員工獲得職業發展建議
  Given 我有一位績效評分 0.9 的資深工程師
  When 我提交其完整資料進行 AI 分析
  Then 我應該收到包含具體職業發展路徑的專業建議
  And 分析信心度應該超過 85%
```

### 共同語言建立

#### 業務詞彙表
| 業務術語 | 技術術語 | 定義 |
|----------|----------|------|
| 員工分析 | Employee Analysis | 對個別員工進行能力評估和發展建議 |
| 團隊動態 | Team Dynamics | 團隊內部協作模式和效能評估 |
| 認知負荷 | Cognitive Load | 用戶處理信息時的心理工作量 |
| 偏見檢測 | Bias Detection | 自動識別評估中的不公平傾向 |
| 信心度 | Confidence Score | AI 分析結果的可信度指標 |

### 協作流程

#### Three Amigos 會議
定期舉行產品經理、開發者、測試者三方會議：

1. **需求澄清**: 確保對功能需求理解一致
2. **場景設計**: 共同撰寫 BDD 場景
3. **接受標準**: 定義功能完成的標準
4. **風險識別**: 討論可能的技術和業務風險

#### 場景審查檢查清單
- [ ] 場景標題清楚描述業務價值
- [ ] Given-When-Then 結構正確
- [ ] 使用業務語言而非技術術語
- [ ] 包含具體的可驗證標準
- [ ] 涵蓋正常流程和異常情況
- [ ] 場景大小適中，不會過於複雜

---

此 BDD 框架為 HR AI 平台建立了完整的行為驅動開發規範，確保產品開發始終以用戶價值為中心，同時促進團隊協作和溝通。