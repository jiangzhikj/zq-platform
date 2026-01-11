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
    horizontal,
    stack,
    barWidth,
    barRadius,
    showBackground,
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

  const baseOption: Record<string, any> = {
    color: colors || ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    legend: legendConfig,
    grid: {
      left: `${gridLeft ?? 3}%`,
      right: `${gridRight ?? 4}%`,
      bottom: `${finalBottom}%`,
      top: `${finalTop}%`,
      containLabel: true,
    },
    series: (seriesData || []).map((s: any) => ({
      name: s.name,
      type: 'bar',
      data: s.data,
      stack: stack ? 'total' : undefined,
      barWidth: barWidth === 'auto' ? undefined : barWidth,
      showBackground,
      backgroundStyle: showBackground
        ? { color: 'rgba(180, 180, 180, 0.2)' }
        : undefined,
      itemStyle: {
        borderRadius: barRadius || 0,
      },
    })),
  };

  if (horizontal) {
    baseOption.xAxis = {
      type: 'value',
      name: yAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 25 : 5,
    };
    baseOption.yAxis = {
      type: 'category',
      data: xAxisData || [],
      name: xAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 40 : 5,
    };
  } else {
    baseOption.xAxis = {
      type: 'category',
      data: xAxisData || [],
      name: xAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 25 : 5,
    };
    baseOption.yAxis = {
      type: 'value',
      name: yAxisName || '',
      nameLocation,
      nameGap: nameLocation === 'middle' ? 40 : 5,
    };
  }

  renderEcharts(baseOption);
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-bar flex h-full flex-col p-3">
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
