<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{
  widget: DashboardWidget;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const renderChart = () => {
  const { nodes, links, colors } = props.widget.props;

  renderEcharts({
    color: colors || ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return params.name;
        }
        return `${params.data.source} → ${params.data.target}: ${params.data.value}`;
      },
    },
    series: [
      {
        type: 'sankey',
        emphasis: {
          focus: 'adjacency',
        },
        left: '5%',
        right: '15%',
        top: '10%',
        bottom: '10%',
        nodeWidth: 20,
        nodeGap: 12,
        lineStyle: {
          color: 'gradient',
          curveness: 0.5,
        },
        label: {
          position: 'right',
          fontSize: 12,
        },
        data: nodes || [],
        links: links || [],
      },
    ],
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-sankey flex h-full flex-col p-3">
    <div class="text-muted-foreground mb-2 text-sm font-medium">
      {{ widget.props.title }}
    </div>
    <div class="min-h-0 flex-1">
      <EchartsUI ref="chartRef" class="h-full w-full" />
    </div>
  </div>
</template>
