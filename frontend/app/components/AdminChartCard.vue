<script setup lang="ts">
type ChartRow = { label: string; value: number; detail?: string }
type ChartMode = 'line' | 'bar' | 'donut'
const props = withDefaults(defineProps<{
  title: string
  subtitle?: string
  rows: ChartRow[]
  mode?: ChartMode
  valuePrefix?: string
  valueSuffix?: string
  filename?: string
}>(), { subtitle: '', mode: 'line', valuePrefix: '', valueSuffix: '', filename: 'nova-home-chart' })
const svgRef = ref<SVGSVGElement | null>(null)
const activeIndex = ref<number | null>(null)
const width = 760
const height = 260
const left = 54
const right = 24
const top = 22
const bottom = 48
const maxValue = computed(() => Math.max(1, ...props.rows.map(row => Number(row.value) || 0)) * 1.12)
const total = computed(() => props.rows.reduce((sum, row) => sum + Math.max(0, Number(row.value) || 0), 0))
const palette = ['#ed1c24', '#f47b80', '#aeb4bc', '#c9151d', '#6d747d', '#f5b7ba']
const points = computed(() => props.rows.map((row, index) => {
  const x = props.rows.length <= 1 ? (left + width - right) / 2 : left + index * ((width - left - right) / (props.rows.length - 1))
  const y = height - bottom - (Number(row.value) / maxValue.value) * (height - top - bottom)
  return { x, y, row }
}))
const polyline = computed(() => points.value.map(point => `${point.x},${point.y}`).join(' '))
const areaPath = computed(() => {
  if (!points.value.length) return ''
  const first = points.value[0]!
  const last = points.value[points.value.length - 1]!
  return `M ${first.x} ${height - bottom} L ${points.value.map(point => `${point.x} ${point.y}`).join(' L ')} L ${last.x} ${height - bottom} Z`
})
const chartBars = computed(() => props.rows.map((row, index) => {
  const band = (height - top - bottom) / Math.max(1, props.rows.length)
  const barWidth = Math.max(0, ((width - left - right) * Math.max(0, Number(row.value))) / maxValue.value)
  return { y: top + index * band + 5, h: Math.max(8, band - 10), w: barWidth, row, index }
}))
const donutSegments = computed(() => {
  const radius = 78
  const circumference = 2 * Math.PI * radius
  let offset = 0
  return props.rows.map((row, index) => {
    const portion = total.value > 0 ? Math.max(0, Number(row.value)) / total.value : 0
    const length = portion * circumference
    const segment = { ...row, index, color: palette[index % palette.length], dash: `${length} ${circumference - length}`, offset: -offset, percentage: portion * 100 }
    offset += length
    return segment
  })
})
function csvEscape(value: unknown) {
  const text = String(value ?? '')
  const safe = /^[=+@\-\t\r]/.test(text) ? `'${text}` : text
  return `"${safe.replaceAll('"', '""')}"`
}
function downloadCsv() {
  const lines = [['Label', 'Value', 'Detail'], ...props.rows.map(row => [row.label, row.value, row.detail || ''])]
  const blob = new Blob(['\ufeff' + lines.map(line => line.map(csvEscape).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${props.filename}.csv`
  link.click()
  URL.revokeObjectURL(url)
}
async function downloadPng() {
  const svg = svgRef.value
  if (!svg) return
  const clone = svg.cloneNode(true) as SVGSVGElement
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg')
  clone.setAttribute('width', String(width))
  clone.setAttribute('height', String(height))
  const style = document.createElementNS('http://www.w3.org/2000/svg', 'style')
  style.textContent = 'text{font-family:Arial,sans-serif;font-size:12px;fill:#41464d}.chart-value-text{font-weight:700}.chart-tooltip-text{font-size:13px;font-weight:700;fill:#ed1c24}.chart-donut-total{font-size:30px;font-weight:700;fill:#20242a}.chart-donut-caption{font-size:12px;fill:#747d86}'
  clone.prepend(style)
  const source = new XMLSerializer().serializeToString(clone)
  const blob = new Blob([source], { type: 'image/svg+xml;charset=utf-8' })
  const objectUrl = URL.createObjectURL(blob)
  try {
    const image = new Image()
    image.src = objectUrl
    await image.decode()
    const canvas = document.createElement('canvas')
    canvas.width = width * 2
    canvas.height = height * 2
    const context = canvas.getContext('2d')
    if (!context) throw new Error('Canvas is unavailable')
    context.scale(2, 2)
    context.fillStyle = '#ffffff'
    context.fillRect(0, 0, width, height)
    context.drawImage(image, 0, 0, width, height)
    const png = await new Promise<Blob>((resolve, reject) => canvas.toBlob(value => value ? resolve(value) : reject(new Error('PNG export failed')), 'image/png'))
    const pngUrl = URL.createObjectURL(png)
    const link = document.createElement('a')
    link.href = pngUrl
    link.download = `${props.filename}.png`
    link.click()
    URL.revokeObjectURL(pngUrl)
  } finally {
    URL.revokeObjectURL(objectUrl)
  }
}
</script>

<template>
  <section class="admin-panel admin-chart-panel">
    <div class="admin-panel-heading">
      <div><h2>{{ title }}</h2><p>{{ subtitle }}</p></div>
      <div class="admin-chart-actions"><button type="button" title="Download chart as CSV" @click="downloadCsv">↓ CSV</button><button type="button" title="Download chart as PNG" @click="downloadPng">↓ PNG</button></div>
    </div>
    <div v-if="rows.length" class="admin-chart-canvas">
      <svg ref="svgRef" viewBox="0 0 760 260" role="img" :aria-label="title">
        <g v-if="mode !== 'donut'" class="chart-grid-lines"><line v-for="line in 4" :key="line" :x1="left" :x2="width-right" :y1="top + (line-1) * ((height-top-bottom)/3)" :y2="top + (line-1) * ((height-top-bottom)/3)" /></g>
        <template v-if="mode === 'line'">
          <path :d="areaPath" fill="rgba(237,28,36,.10)" />
          <polyline :points="polyline" fill="none" stroke="#ed1c24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" />
          <g v-for="(point, index) in points" :key="`${point.row.label}-${index}`" tabindex="0" role="button" :aria-label="`${point.row.label}: ${point.row.value}`" @mouseenter="activeIndex = index" @mouseleave="activeIndex = null" @focus="activeIndex = index" @blur="activeIndex = null">
            <circle :cx="point.x" :cy="point.y" r="15" fill="transparent" />
            <circle :cx="point.x" :cy="point.y" :r="activeIndex === index ? 7 : 5" fill="#ed1c24" stroke="#fff" stroke-width="3" />
            <title>{{ point.row.label }}: {{ valuePrefix }}{{ Number(point.row.value).toLocaleString() }}{{ valueSuffix }}</title>
            <text v-if="index === 0 || index === points.length-1 || activeIndex === index || points.length < 9" :x="point.x" :y="height-18" text-anchor="middle">{{ point.row.label }}</text>
            <text v-if="activeIndex === index" class="chart-tooltip-text" :x="point.x" :y="Math.max(14, point.y-16)" text-anchor="middle">{{ valuePrefix }}{{ Number(point.row.value).toLocaleString() }}{{ valueSuffix }}</text>
          </g>
        </template>
        <template v-else-if="mode === 'bar'">
          <g v-for="bar in chartBars" :key="bar.row.label" tabindex="0" role="button" :aria-label="`${bar.row.label}: ${bar.row.value}`" @mouseenter="activeIndex = bar.index" @mouseleave="activeIndex = null" @focus="activeIndex = bar.index" @blur="activeIndex = null">
            <rect :x="left" :y="bar.y" :width="width-left-right" :height="bar.h" rx="6" fill="#f2f3f5" />
            <rect :x="left" :y="bar.y" :width="bar.w" :height="bar.h" rx="6" fill="#ed1c24" :opacity="activeIndex === bar.index ? 1 : .82" />
            <text x="12" :y="bar.y + bar.h/2 + 4">{{ bar.row.label.slice(0, 25) }}</text>
            <text :x="Math.min(width-right, left+bar.w+10)" :y="bar.y + bar.h/2 + 4" class="chart-value-text">{{ valuePrefix }}{{ Number(bar.row.value).toLocaleString() }}{{ valueSuffix }}</text>
            <title>{{ bar.row.label }}: {{ valuePrefix }}{{ Number(bar.row.value).toLocaleString() }}{{ valueSuffix }} · {{ bar.row.detail || '' }}</title>
          </g>
        </template>
        <template v-else>
          <circle cx="380" cy="126" r="78" fill="none" stroke="#f0f1f3" stroke-width="30" />
          <circle v-for="segment in donutSegments" :key="segment.label" tabindex="0" role="button" :aria-label="`${segment.label}: ${segment.value}`" cx="380" cy="126" r="78" fill="none" :stroke="segment.color" stroke-width="30" stroke-linecap="butt" :stroke-dasharray="segment.dash" :stroke-dashoffset="segment.offset" transform="rotate(-90 380 126)" @mouseenter="activeIndex = segment.index" @mouseleave="activeIndex = null" @focus="activeIndex = segment.index" @blur="activeIndex = null">
            <title>{{ segment.label }}: {{ segment.value }} ({{ segment.percentage.toFixed(1) }}%)</title>
          </circle>
          <circle cx="380" cy="126" r="57" fill="#fff" />
          <text class="chart-donut-total" x="380" y="120" text-anchor="middle">{{ total.toLocaleString() }}</text>
          <text class="chart-donut-caption" x="380" y="145" text-anchor="middle">Total records</text>
          <g v-for="(segment,index) in donutSegments" :key="`legend-${segment.label}`" tabindex="0" role="button" :aria-label="`${segment.label}: ${segment.value}`" @mouseenter="activeIndex = index" @mouseleave="activeIndex = null" @focus="activeIndex = index" @blur="activeIndex = null">
            <circle :cx="230 + (index%2)*300" :cy="220 + Math.floor(index/2)*20" r="5" :fill="segment.color" />
            <text :x="242 + (index%2)*300" :y="224 + Math.floor(index/2)*20">{{ segment.label.slice(0, 22) }} · {{ segment.value }}</text>
          </g>
        </template>
      </svg>
      <div v-if="activeIndex !== null && rows[activeIndex]" class="admin-chart-detail"><b>{{ rows[activeIndex].label }}</b><span>{{ valuePrefix }}{{ Number(rows[activeIndex].value).toLocaleString() }}{{ valueSuffix }}</span><small>{{ rows[activeIndex].detail }}</small></div>
    </div>
    <div v-else class="admin-empty-chart"><span>⌁</span><b>No recorded activity in this period</b><small>Store metrics will appear here as customers browse and shop.</small></div>
  </section>
</template>
