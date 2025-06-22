/**
 * CognitiveButton 組件測試
 * 基於 TDD 原則的單元測試
 */

import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import CognitiveButton from '../CognitiveButton.vue'

describe('CognitiveButton', () => {
  it('should render correctly with default props', () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: 'Test Button'
      }
    })

    expect(wrapper.text()).toContain('Test Button')
    expect(wrapper.classes()).toContain('inline-flex')
    expect(wrapper.classes()).toContain('bg-cognitive-primary')
  })

  it('should apply correct variant classes', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        variant: 'secondary'
      },
      slots: {
        default: 'Secondary Button'
      }
    })

    expect(wrapper.classes()).toContain('bg-white')
    expect(wrapper.classes()).toContain('text-cognitive-neutral')
  })

  it('should apply correct size classes', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        size: 'large'
      },
      slots: {
        default: 'Large Button'
      }
    })

    expect(wrapper.classes()).toContain('px-6')
    expect(wrapper.classes()).toContain('py-3')
    expect(wrapper.classes()).toContain('text-lg')
  })

  it('should be disabled when disabled prop is true', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        disabled: true
      },
      slots: {
        default: 'Disabled Button'
      }
    })

    expect(wrapper.element.disabled).toBe(true)
    expect(wrapper.classes()).toContain('opacity-50')
    expect(wrapper.classes()).toContain('cursor-not-allowed')
  })

  it('should show loading indicator when isLoading is true', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        isLoading: true
      },
      slots: {
        default: 'Loading Button'
      }
    })

    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.find('.animate-spin').exists()).toBe(true)
    expect(wrapper.element.disabled).toBe(true)
  })

  it('should emit click event when clicked', async () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: 'Clickable Button'
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('should not emit click event when disabled', async () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        disabled: true
      },
      slots: {
        default: 'Disabled Button'
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('should not emit click event when loading', async () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        isLoading: true
      },
      slots: {
        default: 'Loading Button'
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeFalsy()
  })

  it('should display icon when provided', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        icon: '<svg class="test-icon"></svg>'
      },
      slots: {
        default: 'Icon Button'
      }
    })

    expect(wrapper.find('.test-icon').exists()).toBe(true)
  })

  it('should emit focus and blur events', async () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: 'Focus Button'
      }
    })

    await wrapper.trigger('focus')
    expect(wrapper.emitted('focus')).toBeTruthy()

    await wrapper.trigger('blur')
    expect(wrapper.emitted('blur')).toBeTruthy()
  })

  it('should have correct aria attributes', () => {
    const wrapper = mount(CognitiveButton, {
      props: {
        isLoading: true,
        ariaDescribedBy: 'help-text'
      },
      slots: {
        default: 'Accessible Button'
      }
    })

    expect(wrapper.attributes('aria-busy')).toBe('true')
    expect(wrapper.attributes('aria-describedby')).toBe('help-text')
  })

  it('should expose focus and blur methods', () => {
    const wrapper = mount(CognitiveButton, {
      slots: {
        default: 'Exposed Methods Button'
      }
    })

    expect(wrapper.vm.focus).toBeDefined()
    expect(wrapper.vm.blur).toBeDefined()
  })
})