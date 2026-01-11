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

// 计算移动平均线
const calculateMA = (data: number[][], dayCount: number) => {
  const result: (number | string)[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < dayCount - 1) {
      result.push('-');
      continue;
    }
    let sum = 0;
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j]?.[1] ?? 0; // 收盘价
    }
    result.push(+(sum / dayCount).toFixed(2));
  }
  return result;
};

const renderChart = () => {
  const {
    xAxisData,
    seriesData,
    showMA5,
    showMA10,
    gridLeft,
    gridRight,
    gridTop,
    gridBottom,
  } = props.widget.props;

  const series: any[] = [
    {
      name: 'K线',
      type: 'candlestick',
      data: seriesData || [],
      itemStyle: {
        color: '#ec0000',
        color0: '#00da3c',
        borderColor: '#ec0000',
        borderColor0: '#00da3c',
      },
    },
  ];

  // 添加 MA5
  if (showMA5 && seriesData?.length >= 5) {
    series.push({
      name: 'MA5',
      type: 'line',
      data: calculateMA(seriesData, 5),
      smooth: true,
      lineStyle: {
        opacity: 0.8,
        width: 1,
      },
      symbol: 'none',
    });
  }

  // 添加 MA10
  if (showMA10 && seriesData?.length >= 10) {
    series.push({
      name: 'MA10',
      type: 'line',
      data: calculateMA(seriesData, 10),
      smooth: true,
      lineStyle: {
        opacity: 0.8,
        width: 1,
      },
      symbol: 'none',
    });
  }

  renderEcharts({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
      },
      formatter: (params: any) => {
        const kline = params.find((p: any) => p.seriesName === 'K线');
        if (!kline) return '';
        const [open, close, low, high] = kline.data;
        let html = `${kline.axisValue}<br/>`;
        html += `开盘: ${open}<br/>`;
        html += `收盘: ${close}<br/>`;
        html += `最低: ${low}<br/>`;
        html += `最高: ${high}<br/>`;
        params.forEach((p: any) => {
          if (p.seriesName !== 'K线' && p.data !== '-') {
            html += `${p.seriesName}: ${p.data}<br/>`;
          }
        });
        return html;
      },
    },
    legend: {
      show: true,
      top: 0,
      data: ['K线', ...(showMA5 ? ['MA5'] : []), ...(showMA10 ? ['MA10'] : [])],
    },
    grid: {
      left: `${gridLeft ?? 3}%`,
      right: `${gridRight ?? 3}%`,
      bottom: `${gridBottom ?? 3}%`,
      top: `${gridTop ?? 15}%`,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: xAxisData || [],
      boundaryGap: true,
      axisLine: { onZero: false },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      scale: true,
      splitArea: {
        show: true,
      },
    },
    series,
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-kline flex h-full flex-col p-3">
    <div class="text-muted-foreground mb-2 text-sm font-medium">
      {{ widget.props.title }}
    </div>
    <div class="min-h-0 flex-1">
      <EchartsUI ref="chartRef" class="h-full w-full" />
    </div>
  </div>
</template>
