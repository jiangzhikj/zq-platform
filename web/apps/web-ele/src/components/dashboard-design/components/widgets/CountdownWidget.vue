<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { onMounted, onUnmounted, ref } from 'vue';

import { $t } from '@vben/locales';

const props = defineProps<{
  widget: DashboardWidget;
}>();

// 剩余时间
const remainingTime = ref({
  days: 0,
  hours: 0,
  minutes: 0,
  seconds: 0,
  finished: false,
});

let timer: null | ReturnType<typeof setInterval> = null;

const calculateRemaining = () => {
  const targetTime = new Date(props.widget.props.targetTime).getTime();
  const now = Date.now();
  const diff = targetTime - now;

  if (diff <= 0) {
    remainingTime.value = {
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      finished: true,
    };
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
    return;
  }

  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);

  remainingTime.value = { days, hours, minutes, seconds, finished: false };
};

onMounted(() => {
  calculateRemaining();
  timer = setInterval(calculateRemaining, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

const padZero = (num: number) => String(num).padStart(2, '0');
</script>

<template>
  <div class="countdown-widget flex h-full flex-col p-3">
    <div
      v-if="widget.props.title"
      class="text-muted-foreground mb-2 text-sm font-medium"
    >
      {{ widget.props.title }}
    </div>

    <div class="flex flex-1 items-center justify-center">
      <template v-if="!remainingTime.finished">
        <div class="flex items-center gap-2">
          <template v-if="widget.props.showDays">
            <div class="time-block">
              <div class="time-value">{{ remainingTime.days }}</div>
              <div class="time-label">{{ $t('dashboard-design.widgets.countdown.day') }}</div>
            </div>
            <span class="time-separator">:</span>
          </template>

          <template v-if="widget.props.showHours">
            <div class="time-block">
              <div class="time-value">{{ padZero(remainingTime.hours) }}</div>
              <div class="time-label">{{ $t('dashboard-design.widgets.countdown.hour') }}</div>
            </div>
            <span class="time-separator">:</span>
          </template>

          <template v-if="widget.props.showMinutes">
            <div class="time-block">
              <div class="time-value">{{ padZero(remainingTime.minutes) }}</div>
              <div class="time-label">{{ $t('dashboard-design.widgets.countdown.minute') }}</div>
            </div>
            <span v-if="widget.props.showSeconds" class="time-separator"
              >:</span
            >
          </template>

          <template v-if="widget.props.showSeconds">
            <div class="time-block">
              <div class="time-value">{{ padZero(remainingTime.seconds) }}</div>
              <div class="time-label">{{ $t('dashboard-design.widgets.countdown.second') }}</div>
            </div>
          </template>
        </div>
      </template>

      <div v-else class="text-muted-foreground text-lg">
        {{ widget.props.finishedText || $t('dashboard-design.widgets.countdown.finished') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.time-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 48px;
}

.time-value {
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1;
  color: var(--el-color-primary);
}

.time-label {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}

.time-separator {
  margin-bottom: 16px;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}
</style>
