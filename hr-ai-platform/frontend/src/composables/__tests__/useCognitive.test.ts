/**
 * useCognitive 組合式函數測試
 * 測試認知友善設計功能
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { 
  COGNITIVE_CONSTANTS,
  useAttention,
  useCognitiveLoad,
  useProgressiveDisclosure,
  useAccessibility,
  useCognitiveAnimation
} from '../useCognitive'

describe('COGNITIVE_CONSTANTS', () => {
  it('should have correct constant values', () => {
    expect(COGNITIVE_CONSTANTS.MAX_VISIBLE_ITEMS).toBe(7)
    expect(COGNITIVE_CONSTANTS.ATTENTION_SPAN_MS).toBe(8000)
    expect(COGNITIVE_CONSTANTS.TIMING.micro).toBe(100)
    expect(COGNITIVE_CONSTANTS.TIMING.quick).toBe(300)
    expect(COGNITIVE_CONSTANTS.TIMING.normal).toBe(500)
    expect(COGNITIVE_CONSTANTS.TIMING.slow).toBe(1000)
  })
})

describe('useAttention', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with correct default values', () => {
    const { isVisible, isFocused, priority } = useAttention()
    
    expect(isVisible.value).toBe(false)
    expect(isFocused.value).toBe(false)
    expect(priority).toBe(2) // normal priority
  })

  it('should set correct priority levels', () => {
    const highPriority = useAttention('high')
    const normalPriority = useAttention('normal')
    const lowPriority = useAttention('low')
    
    expect(highPriority.priority).toBe(1)
    expect(normalPriority.priority).toBe(2)
    expect(lowPriority.priority).toBe(3)
  })

  it('should focus element when focusElement is called', () => {
    const { focusElement, elementRef, isFocused } = useAttention()
    
    const mockElement = {
      focus: vi.fn()
    }
    elementRef.value = mockElement as any
    
    focusElement()
    
    expect(mockElement.focus).toHaveBeenCalled()
    expect(isFocused.value).toBe(true)
  })
})

describe('useCognitiveLoad', () => {
  it('should initialize with correct default values', () => {
    const { currentLoad, maxLoad, loadPercentage } = useCognitiveLoad()
    
    expect(currentLoad).toBe(0)
    expect(maxLoad).toBe(COGNITIVE_CONSTANTS.MAX_VISIBLE_ITEMS)
    expect(loadPercentage).toBe(0)
  })

  it('should add load correctly', () => {
    const { addLoad, currentLoad, loadPercentage } = useCognitiveLoad()
    
    addLoad(3)
    
    expect(currentLoad).toBe(3)
    expect(loadPercentage).toBe((3 / 7) * 100)
  })

  it('should remove load correctly', () => {
    const { addLoad, removeLoad, currentLoad } = useCognitiveLoad()
    
    addLoad(5)
    removeLoad(2)
    
    expect(currentLoad).toBe(3)
  })

  it('should not exceed max load', () => {
    const { addLoad, currentLoad, maxLoad } = useCognitiveLoad()
    
    addLoad(10) // exceeds max
    
    expect(currentLoad).toBe(maxLoad)
  })

  it('should not go below zero', () => {
    const { removeLoad, currentLoad } = useCognitiveLoad()
    
    removeLoad(5) // remove from zero
    
    expect(currentLoad).toBe(0)
  })

  it('should reset load correctly', () => {
    const { addLoad, resetLoad, currentLoad, loadPercentage } = useCognitiveLoad()
    
    addLoad(5)
    resetLoad()
    
    expect(currentLoad).toBe(0)
    expect(loadPercentage).toBe(0)
  })

  it('should detect overload correctly', () => {
    const { addLoad, isOverloaded } = useCognitiveLoad()
    
    expect(isOverloaded).toBe(false)
    
    addLoad(7) // max load
    
    expect(isOverloaded).toBe(true)
  })
})

describe('useProgressiveDisclosure', () => {
  const testSteps = ['Step 1', 'Step 2', 'Step 3', 'Step 4']

  it('should initialize with correct values', () => {
    const { currentStep, totalSteps, completedSteps, progressPercentage } = 
      useProgressiveDisclosure(testSteps)
    
    expect(currentStep).toBe(0)
    expect(totalSteps).toBe(4)
    expect(completedSteps.size).toBe(0)
    expect(progressPercentage).toBe(0)
  })

  it('should navigate to next step correctly', () => {
    const { nextStep, currentStep } = useProgressiveDisclosure(testSteps)
    
    nextStep()
    expect(currentStep).toBe(1)
    
    nextStep()
    expect(currentStep).toBe(2)
  })

  it('should not exceed last step', () => {
    const { nextStep, currentStep, totalSteps } = useProgressiveDisclosure(testSteps)
    
    // Go to last step
    for (let i = 0; i < totalSteps; i++) {
      nextStep()
    }
    
    expect(currentStep).toBe(totalSteps - 1)
  })

  it('should navigate to previous step correctly', () => {
    const { nextStep, prevStep, currentStep } = useProgressiveDisclosure(testSteps)
    
    nextStep()
    nextStep()
    prevStep()
    
    expect(currentStep).toBe(1)
  })

  it('should not go before first step', () => {
    const { prevStep, currentStep } = useProgressiveDisclosure(testSteps)
    
    prevStep()
    
    expect(currentStep).toBe(0)
  })

  it('should go to specific step', () => {
    const { goToStep, currentStep } = useProgressiveDisclosure(testSteps)
    
    goToStep(2)
    expect(currentStep).toBe(2)
  })

  it('should complete steps correctly', () => {
    const { completeStep, isStepCompleted, progressPercentage } = 
      useProgressiveDisclosure(testSteps)
    
    completeStep(0)
    completeStep(1)
    
    expect(isStepCompleted(0)).toBe(true)
    expect(isStepCompleted(1)).toBe(true)
    expect(isStepCompleted(2)).toBe(false)
    expect(progressPercentage).toBe(50) // 2 out of 4 steps
  })
})

describe('useAccessibility', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    document.body.innerHTML = ''
  })

  it('should announce to screen reader', () => {
    const { announceToScreenReader } = useAccessibility()
    
    announceToScreenReader('Test announcement')
    
    const announcement = document.querySelector('[aria-live="polite"]')
    expect(announcement).toBeTruthy()
    expect(announcement?.textContent).toBe('Test announcement')
    expect(announcement?.className).toContain('sr-only')
  })

  it('should trap focus within element', () => {
    const { trapFocus } = useAccessibility()
    
    // Create a test element with focusable children
    const container = document.createElement('div')
    const button1 = document.createElement('button')
    const button2 = document.createElement('button')
    const input = document.createElement('input')
    
    container.appendChild(button1)
    container.appendChild(button2)
    container.appendChild(input)
    document.body.appendChild(container)
    
    const cleanup = trapFocus(container)
    
    expect(cleanup).toBeTypeOf('function')
    
    // Test Tab key handling
    const event = new KeyboardEvent('keydown', { key: 'Tab' })
    Object.defineProperty(document, 'activeElement', {
      value: input,
      writable: true
    })
    
    container.dispatchEvent(event)
    
    cleanup()
  })
})

describe('useCognitiveAnimation', () => {
  beforeEach(() => {
    // Mock matchMedia
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))
  })

  it('should get correct animation duration', () => {
    const { getAnimationDuration, prefersReducedMotion } = useCognitiveAnimation()
    
    prefersReducedMotion.value = false
    expect(getAnimationDuration('normal')).toBe(COGNITIVE_CONSTANTS.TIMING.normal)
    
    prefersReducedMotion.value = true
    expect(getAnimationDuration('normal')).toBe(0)
  })

  it('should create fade transition', () => {
    const { createFadeTransition, prefersReducedMotion } = useCognitiveAnimation()
    
    prefersReducedMotion.value = false
    const transition = createFadeTransition()
    
    expect(transition.enterActiveClass).toBeDefined()
    expect(transition.leaveActiveClass).toBeDefined()
    expect(transition.enterFromClass).toBe('opacity-0')
    expect(transition.leaveToClass).toBe('opacity-0')
  })

  it('should create slide transition', () => {
    const { createSlideTransition, prefersReducedMotion } = useCognitiveAnimation()
    
    prefersReducedMotion.value = false
    const transition = createSlideTransition('up')
    
    expect(transition.enterActiveClass).toBeDefined()
    expect(transition.leaveActiveClass).toBeDefined()
    expect(transition.enterFromClass).toContain('translateY(20px)')
    expect(transition.leaveToClass).toContain('translateY(20px)')
  })

  it('should return empty object when reduced motion is preferred', () => {
    const { createFadeTransition, createSlideTransition, prefersReducedMotion } = 
      useCognitiveAnimation()
    
    prefersReducedMotion.value = true
    
    expect(createFadeTransition()).toEqual({})
    expect(createSlideTransition()).toEqual({})
  })
})