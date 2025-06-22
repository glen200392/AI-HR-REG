/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 認知友善色彩系統
        cognitive: {
          primary: '#2563eb',    // 藍色 - 信任、專業
          success: '#059669',    // 綠色 - 成功、安全  
          warning: '#d97706',    // 橙色 - 注意、謹慎
          danger: '#dc2626',     // 紅色 - 錯誤、緊急
          neutral: '#6b7280',    // 灰色 - 次要信息
          background: '#f8fafc'  // 淺灰 - 減少眼部疲勞
        }
      },
      spacing: {
        // 認知空間系統
        'cognitive-xs': '0.25rem',  // 4px
        'cognitive-sm': '0.5rem',   // 8px
        'cognitive-md': '1rem',     // 16px
        'cognitive-lg': '1.5rem',   // 24px
        'cognitive-xl': '2rem',     // 32px
      },
      fontSize: {
        // 認知字體系統
        'cognitive-xs': ['0.75rem', { lineHeight: '1rem' }],     // 12px
        'cognitive-sm': ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        'cognitive-md': ['1rem', { lineHeight: '1.5rem' }],      // 16px
        'cognitive-lg': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        'cognitive-xl': ['1.25rem', { lineHeight: '1.75rem' }],  // 20px
      },
      boxShadow: {
        // 認知陰影系統
        'cognitive-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'cognitive-md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        'cognitive-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
      },
      animation: {
        // 認知動畫系統
        'cognitive-fade-in': 'fadeIn 0.3s ease-in-out',
        'cognitive-slide-up': 'slideUp 0.5s ease-out',
        'cognitive-pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}