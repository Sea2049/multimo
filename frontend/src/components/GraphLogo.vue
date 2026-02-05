<template>
  <div
    class="graph-logo"
    role="img"
    aria-label="Multimo 图谱风格 Logo"
    :style="{ width: widthStyle, height: heightStyle }"
  >
    <svg
      ref="svgRef"
      class="graph-logo-svg"
      :viewBox="`0 0 ${viewSize} ${viewSize}`"
      preserveAspectRatio="xMidYMid meet"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  width: { type: [String, Number], default: '100%' },
  height: { type: [String, Number], default: '280' }
})

const svgRef = ref(null)
const viewSize = 400

const widthStyle = computed(() =>
  typeof props.width === 'number' ? `${props.width}px` : props.width
)
const heightStyle = computed(() =>
  typeof props.height === 'number' ? `${props.height}px` : props.height
)

// 静态节点与边数据，用于装饰性力导向图（约 20 节点，融入背景的低饱和度配色）
const getStaticGraphData = () => {
  const nodeCount = 20
  const nodes = Array.from({ length: nodeCount }, (_, i) => ({
    id: `n${i}`,
    type: ['a', 'b', 'c'][i % 3]
  }))
  const edges = []
  for (let i = 0; i < nodes.length; i++) {
    const numLinks = 1 + (i % 3)
    for (let k = 0; k < numLinks; k++) {
      const j = (i + 2 + k * 3) % nodeCount
      if (i !== j) edges.push({ source: nodes[i].id, target: nodes[j].id })
    }
  }
  return { nodes, edges }
}

let simulation = null

onMounted(() => {
  if (!svgRef.value) return

  const { nodes, edges } = getStaticGraphData()

  const width = viewSize
  const height = viewSize
  const center = width / 2

  const svg = d3.select(svgRef.value)
  svg.selectAll('*').remove()

  const g = svg.append('g')

  const colorScale = d3.scaleOrdinal()
    .domain(['a', 'b', 'c'])
    .range(['#9CA3B0', '#B0B8C4', '#C4CAD4'])

  simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(d => d.id).distance(70).strength(0.4))
    .force('charge', d3.forceManyBody().strength(-120))
    .force('center', d3.forceCenter(center, center))
    .force('collision', d3.forceCollide().radius(18))
    .force('x', d3.forceX(center).strength(0.06))
    .force('y', d3.forceY(center).strength(0.06))
    .alpha(0.4)
    .restart()

  const link = g.append('g')
    .attr('class', 'graph-logo-links')
    .selectAll('line')
    .data(edges)
    .join('line')
    .attr('stroke', '#A0A8B4')
    .attr('stroke-opacity', 0.55)
    .attr('stroke-width', 1.2)

  const node = g.append('g')
    .attr('class', 'graph-logo-nodes')
    .selectAll('g')
    .data(nodes)
    .join('g')

  node.append('circle')
    .attr('r', 6)
    .attr('fill', d => colorScale(d.type))
    .attr('fill-opacity', 0.7)
    .attr('stroke', 'rgba(255,255,255,0.4)')
    .attr('stroke-width', 1)

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
    node.attr('transform', d => `translate(${d.x},${d.y})`)
  })
})

onUnmounted(() => {
  if (simulation) {
    simulation.stop()
    simulation = null
  }
})
</script>

<style scoped>
.graph-logo {
  display: block;
  overflow: hidden;
}

.graph-logo-svg {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
