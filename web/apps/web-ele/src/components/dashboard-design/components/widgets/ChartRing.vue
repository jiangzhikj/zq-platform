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
  const { seriesData, colors } = props.widget.props;
  const colorList = colors || ['#5470c6', '#91cc75', '#fac858', '#ee6666'];

  // 生成多个环形进度
  const series = (seriesData || []).flatMap((item: any, index: number) => {
    const radius = 90 - index * 25;
    const percent = (item.value / (item.max || 100)) * 100;

    return [
      // 背景环
      {
        type: 'pie',
        radius: [`${radius - 8}%`, `${radius}%`],
        center: ['50%', '50%'],
        silent: true,
        label: { show: false },
        data: [
          {
            value: 100,
            itemStyle: {
              color: 'rgba(128, 128, 128, 0.1)',
            },
          },
        ],
      },
      // 进度环
      {
        type: 'pie',
        radius: [`${radius - 8}%`, `${radius}%`],
        center: ['50%', '50%'],
        startAngle: 90,
        label: {
          show: index === 0,
          position: 'center',
          formatter: () => {
            return `{value|${item.value}}{unit|%}\n{name|${item.name}}`;
          },
          rich: {
            value: {
              fontSize: 28,
              fontWeight: 'bold',
              color: colorList[index % colorList.length],
            },
            unit: {
              fontSize: 14,
              color: '#999',
            },
            name: {
              fontSize: 12,
              color: '#666',
              padding: [5, 0, 0, 0],
            },
          },
        },
        data: [
          {
            value: percent,
            name: item.name,
            itemStyle: {
              color: colorList[index % colorList.length],
              borderRadius: 10,
            },
          },
          {
            value: 100 - percent,
            itemStyle: {
              color: 'transparent',
            },
          },
        ],
      },
    ];
  });

  renderEcharts({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.value === 100 || params.itemStyle?.color === 'transparent')
          return '';
        const item = seriesData?.find((s: any) => s.name === params.name);
        return item ? `${item.name}: ${item.value}/${item.max || 100}` : '';
      },
    },
    legend: {
      show: true,
      bottom: 0,
      data: (seriesData || []).map((s: any) => s.name),
    },
    series,
  });
};

onMounted(renderChart);
watch(() => props.widget.props, renderChart, { deep: true });
</script>

<template>
  <div class="chart-ring flex h-full flex-col p-3">
    <div class="text-muted-foreground mb-2 text-sm font-medium">
      {{ widget.props.title }}
    </div>
    <div class="min-h-0 flex-1">
      <EchartsUI ref="chartRef" class="h-full w-full" />
    </div>
  </div>
</template>
