export type DashboardPeriod = 'week' | 'month' | 'year' | 'custom'

function cairoCalendarDate(now: Date): Date {
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Africa/Cairo', year: 'numeric', month: '2-digit', day: '2-digit',
  }).formatToParts(now)
  const get = (type: string) => Number(parts.find(part => part.type === type)?.value)
  return new Date(Date.UTC(get('year'), get('month') - 1, get('day')))
}

function toDateString(value: Date): string {
  return value.toISOString().slice(0, 10)
}

export function getDashboardDateRange(period: Exclude<DashboardPeriod, 'custom'>, now = new Date()) {
  const cairoToday = cairoCalendarDate(now)
  const start = new Date(cairoToday)
  if (period === 'week') start.setUTCDate(cairoToday.getUTCDate() - ((cairoToday.getUTCDay() + 6) % 7))
  if (period === 'month') start.setUTCDate(1)
  if (period === 'year') start.setUTCMonth(0, 1)
  return { start: toDateString(start), end: toDateString(cairoToday) }
}

function dateAtUtcMidnight(value: string): number {
  const [year, month, day] = value.split('-').map(Number)
  return Date.UTC(year || 1970, (month || 1) - 1, day || 1)
}

export function getDashboardGroupBy(start: string, end: string): 'day' | 'week' | 'month' {
  const span = Math.max(1, Math.round((dateAtUtcMidnight(end) - dateAtUtcMidnight(start)) / 86400000) + 1)
  return span > 120 ? 'month' : span > 35 ? 'week' : 'day'
}

export function formatDashboardDate(value: string): string {
  const dateOnly = value.slice(0, 10)
  const [year, month, day] = dateOnly.split('-').map(Number)
  return new Intl.DateTimeFormat('en-EG', {
    timeZone: 'UTC', month: 'short', day: 'numeric',
  }).format(new Date(Date.UTC(year || 1970, (month || 1) - 1, day || 1)))
}

export function buildCsv(rows: Array<Array<string | number | null | undefined>>): string {
  const escape = (value: unknown) => {
    const text = String(value ?? '')
    // Prefix spreadsheet formula-leading characters to prevent formula injection.
    const safe = /^[=+@\-\t\r]/.test(text) ? `'${text}` : text
    return `"${safe.replaceAll('"', '""')}"`
  }
  return '\ufeff' + rows.map(row => row.map(escape).join(',')).join('\r\n')
}
