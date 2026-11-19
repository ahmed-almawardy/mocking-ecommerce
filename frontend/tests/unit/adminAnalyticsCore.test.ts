import { describe, expect, it } from 'vitest'
import { buildCsv, getDashboardDateRange, getDashboardGroupBy } from '../../app/utils/adminAnalyticsCore'

describe('admin analytics date and export helpers', () => {
  const fixed = new Date(2026, 10, 16, 12, 0, 0)

  it('calculates Monday-to-current-day week ranges', () => {
    expect(getDashboardDateRange('week', fixed)).toEqual({ start: '2026-11-16', end: '2026-11-16' })
  })

  it('uses Cairo local calendar dates even when the browser clock is in UTC', () => {
    const justBeforeUtcMidnight = new Date('2026-11-15T22:30:00.000Z')
    expect(getDashboardDateRange('week', justBeforeUtcMidnight)).toEqual({ start: '2026-11-16', end: '2026-11-16' })
  })

  it('calculates current month and year ranges', () => {
    expect(getDashboardDateRange('month', fixed)).toEqual({ start: '2026-11-01', end: '2026-11-16' })
    expect(getDashboardDateRange('year', fixed)).toEqual({ start: '2026-01-01', end: '2026-11-16' })
  })

  it('selects sensible chart grouping for week, month and year custom ranges', () => {
    expect(getDashboardGroupBy('2026-11-16', '2026-11-22')).toBe('day')
    expect(getDashboardGroupBy('2026-11-01', '2026-11-30')).toBe('day')
    expect(getDashboardGroupBy('2026-01-01', '2026-11-16')).toBe('month')
  })

  it('creates quoted CSV and protects spreadsheet formula-leading values', () => {
    const csv = buildCsv([['Product', 'Value'], ['=IMPORTXML("x")', 10], ['A "quoted" item', 2]])
    expect(csv).toContain(`"'=IMPORTXML(""x"")"`)
    expect(csv).toContain('"A ""quoted"" item"')
  })
})
