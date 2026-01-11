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
    seriesData,
    pieType,
    radius,
    showLabel,
    labelPosition,
    showLegend,
    legendPosition,
    colors,
  } = props.widget.props;

  // 计算半径
  let pieRadius: [string, string] = ['0%', '70%'];
  if (pieType === 'ring') {
    pieRadius = ['40%', '70%'];
  } else if (pieType === 'rose') {
    pieRadius = ['20%', '70%'];
  } else if (radius && Array.isArray(radius) && radius.length === 2) {
    pieRadius = [radius[0], radius[1]];
  }

  // 图例位置配置
  const legendConfig: any = showLegend
    ? {
        show: true,
        ...(legendPosition === 'top' && { top: 0, left: 'center' }),
        ...(legendPosition === 'bottom' && { bottom: 0, left: 'center' }),
        ...(legendPosition === 'left' && {
          left: 0,
          top: 'center',
          orient: 'vertical',
        }),
        ...(legendPosition === 'right' && {
          right: 0,
          top: 'center',
          orient: 'vertical',
        }),
      }
    : { show: false };

  renderEcharts({
    color: colors || ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
    },
    legend: legendConfig,
    series: [
      {
        name: props.widget.props.title,
        type: 'pie',
        radius: pieRadius,
        roseType: pieType === 'rose' ? 'radius' : undefined,
        center: ['50%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: showLabel ?? true,
          position: labelPosition === 'inside' ? 'inside' : 'outside',
          formatter: labelPosition === 'inside' ? '{d}%' : '{b}: {d}%',
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
        labelLine: {
          show: showLabel && labelPosition !== 'inside',
        },
        data: seriesData || [],
      },
    ],
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-pie flex h-full flex-col p-3">
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
