/**
 * 認知友善設計系統
 * 基於認知神經科學的React組件庫
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ===== 認知設計原則常數 =====
const COGNITIVE_CONSTANTS = {
  // 工作記憶限制 (Miller's Law: 7±2)
  MAX_VISIBLE_ITEMS: 7,
  
  // 注意力持續時間 (基於神經科學研究)
  ATTENTION_SPAN_MS: 8000,
  
  // 認知負荷顏色系統
  COLORS: {
    primary: '#2563eb',      // 藍色 - 激活前額葉皮質，增強專注
    success: '#059669',      // 綠色 - 降低皮質醇，減少壓力
    warning: '#d97706',      // 橙色 - 提高警覺性，不過度刺激
    danger: '#dc2626',       // 紅色 - 快速注意捕獲
    neutral: '#6b7280',      // 灰色 - 不爭奪注意力
    background: '#f8fafc'    // 淺灰 - 減少眼部疲勞
  },
  
  // 認知空間系統 (基於格式塔心理學)
  SPACING: {
    xs: '0.25rem',   // 相關元素
    sm: '0.5rem',    // 功能組
    md: '1rem',      // 邏輯區塊
    lg: '1.5rem',    // 主要分組
    xl: '2rem'       // 頁面層級
  },
  
  // 認知時間系統
  TIMING: {
    micro: 100,      // 即時反饋
    quick: 300,      // 快速轉場
    normal: 500,     // 標準動畫
    slow: 1000       // 重要狀態變化
  }
};

// ===== 核心認知鉤子 =====

/**
 * 注意力管理鉤子
 * 基於注意力研究，管理用戶注意力分配
 */
const useAttention = (priority = 'normal') => {
  const [isVisible, setIsVisible] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const elementRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsVisible(entry.isIntersecting),
      { threshold: 0.1 }
    );

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const focusElement = () => {
    if (elementRef.current) {
      elementRef.current.focus();
      setIsFocused(true);
    }
  };

  return {
    elementRef,
    isVisible,
    isFocused,
    focusElement,
    priority: priority === 'high' ? 1 : priority === 'low' ? 3 : 2
  };
};

/**
 * 認知負荷管理鉤子
 * 基於認知負荷理論，動態管理界面複雜度
 */
const useCognitiveLoad = () => {
  const [currentLoad, setCurrentLoad] = useState(0);
  const [maxLoad] = useState(COGNITIVE_CONSTANTS.MAX_VISIBLE_ITEMS);

  const addLoad = (amount = 1) => {
    setCurrentLoad(prev => Math.min(prev + amount, maxLoad));
  };

  const removeLoad = (amount = 1) => {
    setCurrentLoad(prev => Math.max(prev - amount, 0));
  };

  const resetLoad = () => setCurrentLoad(0);

  const isOverloaded = currentLoad >= maxLoad;
  const loadPercentage = (currentLoad / maxLoad) * 100;

  return {
    currentLoad,
    maxLoad,
    addLoad,
    removeLoad,
    resetLoad,
    isOverloaded,
    loadPercentage
  };
};

/**
 * 漸進披露鉤子
 * 基於信息架構理論，管理內容的漸進顯示
 */
const useProgressiveDisclosure = (steps) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  };

  const goToStep = (step) => {
    if (step >= 0 && step < steps.length) {
      setCurrentStep(step);
    }
  };

  const completeStep = (step = currentStep) => {
    setCompletedSteps(prev => new Set(prev).add(step));
  };

  const isStepCompleted = (step) => completedSteps.has(step);
  const progressPercentage = (completedSteps.size / steps.length) * 100;

  return {
    currentStep,
    nextStep,
    prevStep,
    goToStep,
    completeStep,
    isStepCompleted,
    progressPercentage,
    totalSteps: steps.length
  };
};

// ===== 認知UI組件 =====

/**
 * 認知按鈕組件
 * 基於行為心理學設計的按鈕系統
 */
const CognitiveButton = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  cognitiveLoad = 1,
  isLoading = false,
  disabled = false,
  onClick,
  ...props 
}) => {
  const attention = useAttention(variant === 'primary' ? 'high' : 'normal');

  const variants = {
    primary: {
      backgroundColor: COGNITIVE_CONSTANTS.COLORS.primary,
      color: 'white',
      border: 'none'
    },
    secondary: {
      backgroundColor: 'transparent',
      color: COGNITIVE_CONSTANTS.COLORS.neutral,
      border: `1px solid ${COGNITIVE_CONSTANTS.COLORS.neutral}`
    },
    success: {
      backgroundColor: COGNITIVE_CONSTANTS.COLORS.success,
      color: 'white',
      border: 'none'
    },
    warning: {
      backgroundColor: COGNITIVE_CONSTANTS.COLORS.warning,
      color: 'white',
      border: 'none'
    }
  };

  const sizes = {
    small: { padding: '0.5rem 1rem', fontSize: '0.875rem' },
    medium: { padding: '0.75rem 1.5rem', fontSize: '1rem' },
    large: { padding: '1rem 2rem', fontSize: '1.125rem' }
  };

  return (
    <motion.button
      ref={attention.elementRef}
      style={{
        ...variants[variant],
        ...sizes[size],
        borderRadius: '0.5rem',
        fontWeight: 500,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        transition: 'all 0.2s ease'
      }}
      whileHover={!disabled ? { scale: 1.02, y: -1 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      onClick={disabled ? undefined : onClick}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          style={{
            width: '16px',
            height: '16px',
            border: '2px solid transparent',
            borderTop: '2px solid currentColor',
            borderRadius: '50%'
          }}
        />
      )}
      {children}
    </motion.button>
  );
};

/**
 * 認知表單組件
 * 基於認知負荷理論的表單設計
 */
const CognitiveForm = ({ children, onSubmit, maxSections = 5 }) => {
  const cognitiveLoad = useCognitiveLoad();
  const [sections, setSections] = useState([]);

  useEffect(() => {
    // 分析表單複雜度
    const formSections = React.Children.count(children);
    cognitiveLoad.resetLoad();
    cognitiveLoad.addLoad(Math.min(formSections, maxSections));
  }, [children]);

  return (
    <form 
      onSubmit={onSubmit}
      style={{
        maxWidth: '600px',
        margin: '0 auto',
        padding: COGNITIVE_CONSTANTS.SPACING.lg
      }}
    >
      {/* 認知負荷指示器 */}
      {cognitiveLoad.isOverloaded && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            backgroundColor: COGNITIVE_CONSTANTS.COLORS.warning,
            color: 'white',
            padding: COGNITIVE_CONSTANTS.SPACING.sm,
            borderRadius: '0.5rem',
            marginBottom: COGNITIVE_CONSTANTS.SPACING.md,
            fontSize: '0.875rem'
          }}
        >
          ⚠️ 表單較為複雜，建議分步驟填寫
        </motion.div>
      )}

      {children}

      {/* 進度指示 */}
      <div style={{
        marginTop: COGNITIVE_CONSTANTS.SPACING.lg,
        height: '4px',
        backgroundColor: '#e5e7eb',
        borderRadius: '2px',
        overflow: 'hidden'
      }}>
        <motion.div
          style={{
            height: '100%',
            backgroundColor: COGNITIVE_CONSTANTS.COLORS.primary
          }}
          initial={{ width: 0 }}
          animate={{ width: `${cognitiveLoad.loadPercentage}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </form>
  );
};

/**
 * 認知導航組件
 * 基於空間認知的導航設計
 */
const CognitiveNavigation = ({ items, currentPath, onNavigate }) => {
  const attention = useAttention('high');

  return (
    <nav 
      ref={attention.elementRef}
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: COGNITIVE_CONSTANTS.SPACING.lg,
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}
    >
      {items.map((item, index) => (
        <motion.div
          key={item.path}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: COGNITIVE_CONSTANTS.SPACING.sm,
            padding: COGNITIVE_CONSTANTS.SPACING.sm,
            borderRadius: '8px',
            cursor: 'pointer',
            marginBottom: COGNITIVE_CONSTANTS.SPACING.xs,
            backgroundColor: currentPath === item.path ? '#dbeafe' : 'transparent',
            color: currentPath === item.path ? COGNITIVE_CONSTANTS.COLORS.primary : '#374151'
          }}
          whileHover={{ backgroundColor: '#f3f4f6', x: 2 }}
          onClick={() => onNavigate(item.path)}
        >
          <span style={{ fontSize: '1.25rem' }}>{item.icon}</span>
          <span style={{ fontWeight: currentPath === item.path ? 500 : 400 }}>
            {item.label}
          </span>
          
          {/* 活動指示器 */}
          {currentPath === item.path && (
            <motion.div
              layoutId="activeIndicator"
              style={{
                position: 'absolute',
                left: 0,
                width: '3px',
                height: '20px',
                backgroundColor: COGNITIVE_CONSTANTS.COLORS.primary,
                borderRadius: '2px'
              }}
            />
          )}
        </motion.div>
      ))}
    </nav>
  );
};

/**
 * 認知結果展示組件
 * 基於信息處理理論的結果呈現
 */
const CognitiveResults = ({ data, isLoading = false }) => {
  const disclosure = useProgressiveDisclosure(['overview', 'details', 'actions']);

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: COGNITIVE_CONSTANTS.SPACING.xl,
          backgroundColor: 'white',
          borderRadius: '12px'
        }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          style={{
            width: '40px',
            height: '40px',
            border: '3px solid #f3f4f6',
            borderTop: '3px solid ' + COGNITIVE_CONSTANTS.COLORS.primary,
            borderRadius: '50%',
            marginBottom: COGNITIVE_CONSTANTS.SPACING.md
          }}
        />
        <p style={{ color: COGNITIVE_CONSTANTS.COLORS.neutral }}>
          AI 正在分析中，請稍候...
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        overflow: 'hidden',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}
    >
      {/* 結果頭部 */}
      <div style={{
        padding: COGNITIVE_CONSTANTS.SPACING.lg,
        borderBottom: '1px solid #e5e7eb',
        background: 'linear-gradient(90deg, #f8fafc 0%, #f1f5f9 100%)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ 
            fontSize: '1.25rem', 
            fontWeight: 600,
            color: '#1f2937'
          }}>
            🎯 分析結果
          </h3>
          <div style={{
            padding: '0.25rem 0.75rem',
            backgroundColor: '#dcfce7',
            color: COGNITIVE_CONSTANTS.COLORS.success,
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 500
          }}>
            信心度: {data?.confidence || 87}%
          </div>
        </div>

        {/* 步驟指示器 */}
        <div style={{
          display: 'flex',
          gap: COGNITIVE_CONSTANTS.SPACING.sm,
          marginTop: COGNITIVE_CONSTANTS.SPACING.md
        }}>
          {['概覽', '詳細', '行動'].map((step, index) => (
            <motion.div
              key={step}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '20px',
                fontSize: '0.875rem',
                cursor: 'pointer',
                backgroundColor: disclosure.currentStep === index ? '#dbeafe' : '#f3f4f6',
                color: disclosure.currentStep === index ? COGNITIVE_CONSTANTS.COLORS.primary : COGNITIVE_CONSTANTS.COLORS.neutral
              }}
              whileHover={{ scale: 1.05 }}
              onClick={() => disclosure.goToStep(index)}
            >
              {step}
            </motion.div>
          ))}
        </div>
      </div>

      {/* 結果內容 */}
      <div style={{ padding: COGNITIVE_CONSTANTS.SPACING.lg }}>
        <AnimatePresence mode="wait">
          {disclosure.currentStep === 0 && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h4 style={{ color: COGNITIVE_CONSTANTS.COLORS.primary, marginBottom: COGNITIVE_CONSTANTS.SPACING.md }}>
                📊 分析概覽
              </h4>
              <p>{data?.summary || '基於員工資料的綜合分析顯示積極的發展潛力。'}</p>
            </motion.div>
          )}

          {disclosure.currentStep === 1 && (
            <motion.div
              key="details"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h4 style={{ color: COGNITIVE_CONSTANTS.COLORS.success, marginBottom: COGNITIVE_CONSTANTS.SPACING.md }}>
                ⭐ 詳細分析
              </h4>
              <div>
                {data?.details?.map((detail, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    style={{ marginBottom: COGNITIVE_CONSTANTS.SPACING.sm }}
                  >
                    • {detail}
                  </motion.div>
                )) || (
                  <>
                    <div>• 技術能力突出，學習能力強</div>
                    <div>• 團隊協作表現優異</div>
                    <div>• 具備良好的發展潛力</div>
                  </>
                )}
              </div>
            </motion.div>
          )}

          {disclosure.currentStep === 2 && (
            <motion.div
              key="actions"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <h4 style={{ color: COGNITIVE_CONSTANTS.COLORS.warning, marginBottom: COGNITIVE_CONSTANTS.SPACING.md }}>
                🚀 建議行動
              </h4>
              <div style={{
                display: 'flex',
                gap: COGNITIVE_CONSTANTS.SPACING.sm,
                flexWrap: 'wrap'
              }}>
                <CognitiveButton variant="primary" size="small">
                  📄 下載報告
                </CognitiveButton>
                <CognitiveButton variant="secondary" size="small">
                  📧 分享結果
                </CognitiveButton>
                <CognitiveButton variant="secondary" size="small">
                  📅 安排面談
                </CognitiveButton>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* 導航控制 */}
      <div style={{
        padding: COGNITIVE_CONSTANTS.SPACING.md,
        borderTop: '1px solid #e5e7eb',
        display: 'flex',
        justifyContent: 'space-between'
      }}>
        <CognitiveButton
          variant="secondary"
          size="small"
          disabled={disclosure.currentStep === 0}
          onClick={disclosure.prevStep}
        >
          上一步
        </CognitiveButton>
        
        <CognitiveButton
          variant="secondary" 
          size="small"
          disabled={disclosure.currentStep === disclosure.totalSteps - 1}
          onClick={disclosure.nextStep}
        >
          下一步
        </CognitiveButton>
      </div>
    </motion.div>
  );
};

/**
 * 主要HR分析應用組件
 */
const HRAnalysisApp = () => {
  const [currentView, setCurrentView] = useState('employee');
  const [analysisData, setAnalysisData] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const navigationItems = [
    { path: 'employee', label: '員工分析', icon: '👤' },
    { path: 'team', label: '團隊分析', icon: '👥' },
    { path: 'batch', label: '批量分析', icon: '📊' },
    { path: 'history', label: '歷史記錄', icon: '📋' },
    { path: 'settings', label: '設定', icon: '⚙️' }
  ];

  const handleAnalysis = async (formData) => {
    setIsAnalyzing(true);
    
    try {
      // 模擬API調用
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setAnalysisData({
        confidence: 87,
        summary: '該員工展現出優秀的技術能力和良好的團隊協作精神。',
        details: [
          '技術能力在同級別中排名前25%',
          '具備良好的學習適應能力',
          '團隊協作評分高於平均水平',
          '職業發展方向明確'
        ]
      });
    } catch (error) {
      console.error('分析失敗:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: COGNITIVE_CONSTANTS.COLORS.background,
      padding: COGNITIVE_CONSTANTS.SPACING.md
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: '280px 1fr',
        gap: COGNITIVE_CONSTANTS.SPACING.md
      }}>
        {/* 側邊導航 */}
        <CognitiveNavigation
          items={navigationItems}
          currentPath={currentView}
          onNavigate={setCurrentView}
        />

        {/* 主內容區域 */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          overflow: 'hidden'
        }}>
          {currentView === 'employee' && (
            <div>
              <div style={{
                padding: COGNITIVE_CONSTANTS.SPACING.xl,
                borderBottom: '1px solid #e5e7eb'
              }}>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: COGNITIVE_CONSTANTS.SPACING.sm }}>
                  員工分析
                </h1>
                <p style={{ color: COGNITIVE_CONSTANTS.COLORS.neutral }}>
                  基於AI的專業人才評估與發展建議
                </p>
              </div>

              <div style={{ padding: COGNITIVE_CONSTANTS.SPACING.xl }}>
                <CognitiveForm onSubmit={handleAnalysis}>
                  {/* 表單內容將在這裡渲染 */}
                  <div style={{ marginBottom: COGNITIVE_CONSTANTS.SPACING.lg }}>
                    <label style={{ 
                      display: 'block', 
                      marginBottom: COGNITIVE_CONSTANTS.SPACING.sm,
                      fontWeight: 500
                    }}>
                      員工姓名 *
                    </label>
                    <input
                      type="text"
                      placeholder="請輸入員工姓名"
                      style={{
                        width: '100%',
                        padding: COGNITIVE_CONSTANTS.SPACING.md,
                        border: '1px solid #d1d5db',
                        borderRadius: '8px',
                        fontSize: '1rem'
                      }}
                    />
                  </div>

                  <div style={{ textAlign: 'center', marginTop: COGNITIVE_CONSTANTS.SPACING.xl }}>
                    <CognitiveButton
                      variant="primary"
                      isLoading={isAnalyzing}
                      onClick={handleAnalysis}
                    >
                      🤖 開始 AI 分析
                    </CognitiveButton>
                  </div>
                </CognitiveForm>

                {(analysisData || isAnalyzing) && (
                  <div style={{ marginTop: COGNITIVE_CONSTANTS.SPACING.xl }}>
                    <CognitiveResults data={analysisData} isLoading={isAnalyzing} />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// 導出組件和鉤子
export {
  HRAnalysisApp,
  CognitiveButton,
  CognitiveForm,
  CognitiveNavigation,
  CognitiveResults,
  useAttention,
  useCognitiveLoad,
  useProgressiveDisclosure,
  COGNITIVE_CONSTANTS
};