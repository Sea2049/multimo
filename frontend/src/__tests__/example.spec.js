import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'

describe('Sanity Check', () => {
  it('adds 1 + 1', () => {
    expect(1 + 1).toBe(2)
  })
})

describe('Component Test', () => {
  it('renders properly', () => {
    const wrapper = mount({
      template: '<div>Hello Vitest</div>'
    })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
})
