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
  const {
    xAxisData,
    seriesData,
    smooth,
    showArea,
    showSymbol,
    symbolSize,
    lineWidth,
    showLegend,
    legendPosition,
    colors,
    xAxisName,
    yAxisName,
    axisNameLocation,
    gridLeft,
    gridRight,
    gridTop,
    gridBottom,
  } = props.widget.props;

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

  // 坐标轴名称位置
  const nameLocation = axisNameLocation || 'end';

  // 计算 grid 边距
  let finalBottom = gridBottom ?? 3;
  let finalTop = gridTop ?? 10;
  if (showLegend && legendPosition === 'bottom') finalBottom += 12;
  if (showLegend && legendPosition === 'top') finalTop += 5;

  renderEcharts({
    color: colors || ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    tooltip: {
      trigger: 'axis',
    },
    legend: legendConfig,
    grid: {
      left: `${gridLeft ?? 3}%`,
      right: `${gridRight ?? 4}%`,
      bottom: `${finalBottom}%`,
      top: `${finalTop}%`,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xAxisData || [],
      name: xAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 25 : 5,
    },
    yAxis: {
      type: 'value',
      name: yAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 40 : 5,
    },
    series: (seriesData || []).map((s: any) => ({
      name: s.name,
      type: 'line',
      smooth: smooth ?? true,
      showSymbol: showSymbol ?? true,
      symbolSize: symbolSize || 6,
      lineStyle: {
        width: lineWidth || 2,
      },
      areaStyle: showArea ? { opacity: 0.3 } : undefined,
      data: s.data,
    })),
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-line flex h-full flex-col p-3">
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
