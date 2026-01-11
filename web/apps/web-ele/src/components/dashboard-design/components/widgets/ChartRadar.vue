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
  const { indicators, seriesData, shape, showLegend, legendPosition, colors } =
    props.widget.props;

  // 图例位置配置
  const legendConfig: any = showLegend
    ? {
        show: true,
        ...(legendPosition === 'top' && { top: 0 }),
        ...(legendPosition === 'bottom' && { bottom: 0 }),
        ...(legendPosition === 'left' && { left: 0, orient: 'vertical' }),
        ...(legendPosition === 'right' && { right: 0, orient: 'vertical' }),
      }
    : { show: false };

  renderEcharts({
    color: colors || ['#5470c6', '#91cc75', '#fac858'],
    tooltip: {
      trigger: 'item',
    },
    legend: legendConfig,
    radar: {
      shape: shape || 'polygon',
      indicator: indicators || [],
      center: ['50%', '55%'],
      radius: '65%',
    },
    series: [
      {
        type: 'radar',
        data: (seriesData || []).map((s: any) => ({
          name: s.name,
          value: s.value,
          areaStyle: {
            opacity: 0.2,
          },
        })),
      },
    ],
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-radar flex h-full flex-col p-3">
    <div class="text-muted-foreground mb-2 text-sm font-medium">
      {{ widget.props.title }}
    </div>
    <div class="min-h-0 flex-1">
      <EchartsUI ref="chartRef" class="h-full w-full" />
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
