<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed, onMounted, onUnmounted, ref } from 'vue';

import { $t } from '@vben/locales';
import { preferences } from '@vben/preferences';

const props = defineProps<{
  widget: DashboardWidget;
}>();

const locale = computed(() => preferences.app.locale);

const currentTime = ref('');
const currentDate = ref('');

let timer: null | ReturnType<typeof setInterval> = null;

const updateTime = () => {
  const now = new Date();

  // 处理时区
  const date = now;
  if (props.widget.props.timezone && props.widget.props.timezone !== 'local') {
    try {
      const options: Intl.DateTimeFormatOptions = {
        timeZone: props.widget.props.timezone,
        hour: '2-digit',
        minute: '2-digit',
        second: props.widget.props.showSeconds ? '2-digit' : undefined,
        hour12: !props.widget.props.format24,
      };
      currentTime.value = now.toLocaleTimeString(locale.value, options);

      const dateOptions: Intl.DateTimeFormatOptions = {
        timeZone: props.widget.props.timezone,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        weekday: 'short',
      };
      currentDate.value = now.toLocaleDateString(locale.value, dateOptions);
      return;
    } catch {
      // 时区无效，使用本地时间
    }
  }

  // 本地时间
  const hours = props.widget.props.format24
    ? String(date.getHours()).padStart(2, '0')
    : String(date.getHours() % 12 || 12).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  const ampm = props.widget.props.format24
    ? ''
    : date.getHours() >= 12
      ? ' PM'
      : ' AM';

  currentTime.value = props.widget.props.showSeconds
    ? `${hours}:${minutes}:${seconds}${ampm}`
    : `${hours}:${minutes}${ampm}`;

  const weekdays = $t('dashboard-design.widgets.clock.weekdays') as unknown as string[];
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const weekday = weekdays[date.getDay()];
  
  const yearSuffix = $t('dashboard-design.widgets.clock.year');
  const monthSuffix = $t('dashboard-design.widgets.clock.month');
  const daySuffix = $t('dashboard-design.widgets.clock.day');
  
  currentDate.value = `${year}${yearSuffix}${month}${monthSuffix}${day}${daySuffix} ${weekday}`;
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<template>
  <div
    class="clock-widget flex h-full flex-col items-center justify-center p-3"
  >
    <div v-if="widget.props.title" class="text-muted-foreground mb-2 text-sm">
      {{ widget.props.title }}
    </div>

    <div class="time-display">
      {{ currentTime }}
    </div>

    <div v-if="widget.props.showDate" class="date-display">
      {{ currentDate }}
    </div>
  </div>
</template>

<style scoped>
.time-display {
  font-size: 2.5rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
  color: var(--el-text-color-primary);
}

.date-display {
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}
</style>
