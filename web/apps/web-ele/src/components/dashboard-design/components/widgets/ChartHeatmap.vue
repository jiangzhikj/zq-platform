<script setup lang="ts">
import type { EchartsUIType } from '@vben/plugins/echarts';

import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { onMounted, ref, watch } from 'vue';

import { EchartsUI, useEcharts } from '@vben/plugins/echarts';
import { $t } from '@vben/locales';

const props = defineProps<{
  widget: DashboardWidget;
}>();

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const renderChart = () => {
  const {
    xAxisData,
    yAxisData,
    seriesData,
    minValue,
    maxValue,
    gridLeft,
    gridRight,
    gridTop,
    gridBottom,
  } = props.widget.props;

  renderEcharts({
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const x = xAxisData?.[params.value[0]] || params.value[0];
        const y = yAxisData?.[params.value[1]] || params.value[1];
        return `${x} ${y}<br/>${$t('dashboard-design.widgets.chart.visits')}: ${params.value[2]}`;
      },
    },
    grid: {
      left: `${gridLeft ?? 3}%`,
      right: `${gridRight ?? 15}%`,
      bottom: `${gridBottom ?? 3}%`,
      top: `${gridTop ?? 10}%`,
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: xAxisData || [],
      splitArea: {
        show: true,
      },
    },
    yAxis: {
      type: 'category',
      data: yAxisData || [],
      splitArea: {
        show: true,
      },
    },
    visualMap: {
      min: minValue ?? 0,
      max: maxValue ?? 100,
      calculable: true,
      orient: 'vertical',
      right: '2%',
      top: 'center',
      inRange: {
        color: ['#f0f9e8', '#bae4bc', '#7bccc4', '#43a2ca', '#0868ac'],
      },
    },
    series: [
      {
        type: 'heatmap',
        data: seriesData || [],
        label: {
          show: true,
          fontSize: 10,
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-heatmap flex h-full flex-col p-3">
    <div class="text-muted-foreground mb-2 text-sm font-medium">
      {{ widget.props.title }}
    </div>
    <div class="min-h-0 flex-1">
      <EchartsUI ref="chartRef" class="h-full w-full" />
    </div>
  </div>
</template>
