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
    value,
    min,
    max,
    unit,
    splitNumber,
    showProgress,
    colorStops,
    pointerWidth,
    pointerLength,
  } = props.widget.props;

  // 颜色渐变配置
  const axisLineColor =
    colorStops && colorStops.length > 0
      ? colorStops.map((stop: any) => [stop.offset, stop.color])
      : [
          [0.3, '#67e0e3'],
          [0.7, '#37a2da'],
          [1, '#fd666d'],
        ];

  renderEcharts({
    series: [
      {
        type: 'gauge',
        min: min ?? 0,
        max: max ?? 100,
        splitNumber: splitNumber ?? 10,
        progress: {
          show: showProgress ?? true,
          width: 18,
        },
        axisLine: {
          lineStyle: {
            width: 18,
            color: axisLineColor,
          },
        },
        axisTick: {
          show: true,
          splitNumber: 5,
          length: 6,
          lineStyle: {
            color: 'auto',
            width: 1,
          },
        },
        splitLine: {
          length: 12,
          lineStyle: {
            width: 2,
            color: 'auto',
          },
        },
        axisLabel: {
          distance: 25,
          color: '#999',
          fontSize: 12,
        },
        pointer: {
          width: pointerWidth || 6,
          length: pointerLength || '60%',
          itemStyle: {
            color: 'auto',
          },
        },
        anchor: {
          show: true,
          showAbove: true,
          size: 18,
          itemStyle: {
            borderWidth: 6,
            borderColor: '#999',
          },
        },
        title: {
          show: false,
        },
        detail: {
          valueAnimation: true,
          fontSize: 28,
          fontWeight: 'bold',
          offsetCenter: [0, '70%'],
          formatter: `{value}${unit || '%'}`,
          color: 'inherit',
        },
        data: [
          {
            value: value ?? 0,
          },
        ],
      },
    ],
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-gauge flex h-full flex-col p-3">
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
