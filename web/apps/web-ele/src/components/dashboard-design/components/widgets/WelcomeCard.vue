<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed, onMounted, onUnmounted, ref } from 'vue';

import { $t } from '@vben/locales';
import { useUserStore } from '@vben/stores';

import { Smile } from '@vben/icons';
import { UserAvatar } from '#/components/user-avatar';

defineProps<{
  widget: DashboardWidget;
}>();

const userStore = useUserStore();

// 用户信息
const userInfo = computed(() => userStore.userInfo);
// 用户名
const userName = computed(() => userStore.userInfo?.realName || '');

const currentTime = ref(new Date());
let timer: null | ReturnType<typeof setInterval> = null;

onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});

const greeting = computed(() => {
  const hour = currentTime.value.getHours();
  if (hour < 6) return $t('dashboard-design.widgets.welcome.greeting.night');
  if (hour < 9) return $t('dashboard-design.widgets.welcome.greeting.morning');
  if (hour < 12) return $t('dashboard-design.widgets.welcome.greeting.morning2');
  if (hour < 14) return $t('dashboard-design.widgets.welcome.greeting.noon');
  if (hour < 18) return $t('dashboard-design.widgets.welcome.greeting.afternoon');
  if (hour < 22) return $t('dashboard-design.widgets.welcome.greeting.evening');
  return $t('dashboard-design.widgets.welcome.greeting.night');
});

const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
});

const formattedDate = computed(() => {
  return currentTime.value.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  });
});
</script>

<template>
  <div class="welcome-card flex h-full items-center justify-between p-4">
    <div class="flex items-center gap-4">
      <!-- 用户头像 -->
      <UserAvatar
        v-if="userInfo"
        :name="userName"
        :avatar="userInfo.avatar"
        :size="48"
        :font-size="20"
        :show-popover="false"
        :shadow="false"
        class="flex-shrink-0"
      />
      <div
        v-else
        class="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full"
        style="
          background: linear-gradient(
            135deg,
            var(--el-color-primary-light-3),
            var(--el-color-primary)
          );
        "
      >
        <Smile class="h-6 w-6 text-white" />
      </div>
      <div>
        <div class="text-lg font-semibold">
          {{ greeting }}，{{ userName
          }}{{ widget.props.title ? `，${widget.props.title}` : '' }}
        </div>
        <div class="text-muted-foreground text-sm">
          {{ widget.props.subtitle }}
        </div>
      </div>
    </div>
    <div v-if="widget.props.showTime" class="text-right">
      <div class="text-2xl font-bold tabular-nums">{{ formattedTime }}</div>
      <div class="text-muted-foreground text-sm">{{ formattedDate }}</div>
    </div>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
