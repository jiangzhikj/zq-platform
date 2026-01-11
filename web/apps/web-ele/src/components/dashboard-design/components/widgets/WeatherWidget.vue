<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed } from 'vue';

import {
  Cloud,
  CloudFog,
  CloudRain,
  CloudSnow,
  CloudSun,
  Sun,
} from '@vben/icons';
import { $t } from '@vben/locales';

const props = defineProps<{
  widget: DashboardWidget;
}>();

// 天气图标映射
const weatherIcon = computed(() => {
  const icon = props.widget.props.icon || 'sunny';
  const iconMap: Record<string, any> = {
    sunny: Sun,
    cloudy: Cloud,
    'partly-cloudy': CloudSun,
    rainy: CloudRain,
    snowy: CloudSnow,
    foggy: CloudFog,
  };
  return iconMap[icon] || Sun;
});

// 天气图标颜色
const iconColor = computed(() => {
  const icon = props.widget.props.icon || 'sunny';
  const colorMap: Record<string, string> = {
    sunny: '#f59e0b',
    cloudy: '#9ca3af',
    'partly-cloudy': '#60a5fa',
    rainy: '#3b82f6',
    snowy: '#e5e7eb',
    foggy: '#9ca3af',
  };
  return colorMap[icon] || '#f59e0b';
});
</script>

<template>
  <div class="weather-widget flex h-full flex-col p-3">
    <div
      v-if="widget.props.title"
      class="text-muted-foreground mb-2 text-sm font-medium"
    >
      {{ widget.props.title }}
    </div>

    <div class="flex flex-1 items-center gap-4">
      <!-- 天气图标和温度 -->
      <div class="flex items-center gap-3">
        <component
          :is="weatherIcon"
          class="h-12 w-12"
          :style="{ color: iconColor }"
        />
        <div>
          <div class="temperature">{{ widget.props.temperature }}°</div>
          <div class="weather-text">
            {{ widget.props.weather }}
          </div>
        </div>
      </div>

      <!-- 详细信息 -->
      <div class="weather-details">
        <div class="detail-item">
          <span class="detail-label">{{ $t('dashboard-design.widgets.weather.city') }}</span>
          <span class="detail-value">{{ widget.props.city }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">{{ $t('dashboard-design.widgets.weather.humidity') }}</span>
          <span class="detail-value">{{ widget.props.humidity }}%</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">{{ $t('dashboard-design.widgets.weather.wind') }}</span>
          <span class="detail-value">{{ widget.props.wind }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.temperature {
  font-size: 2rem;
  font-weight: 600;
  line-height: 1;
  color: var(--el-text-color-primary);
}

.weather-text {
  margin-top: 4px;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}

.weather-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-left: 16px;
  border-left: 1px solid var(--el-border-color-lighter);
}

.detail-item {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.75rem;
}

.detail-label {
  min-width: 32px;
  color: var(--el-text-color-secondary);
}

.detail-value {
  color: var(--el-text-color-primary);
}
</style>
