<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import type { UserAnnouncement } from '#/api/core/announcement';

import { computed, onMounted, ref } from 'vue';

import { CheckCheck, Megaphone } from '@vben/icons';
import { $t } from '@vben/locales';

import { ElButton, ElEmpty, ElScrollbar, ElTag } from 'element-plus';

import {
  getUserAnnouncementDetailApi,
  getUserAnnouncementListApi,
} from '#/api/core/announcement';
import { ZqDialog } from '#/components/zq-dialog';

const props = defineProps<{
  widget: DashboardWidget;
}>();

// 实际公告数据
const announcements = ref<UserAnnouncement[]>([]);
const loading = ref(false);

// 详情弹窗
const detailVisible = ref(false);
const currentAnnouncement = ref<null | UserAnnouncement>(null);
const detailLoading = ref(false);

// 未读数量
const unreadCount = computed(
  () => announcements.value.filter((a) => !a.is_read).length,
);

// 获取优先级配置
const getPriorityConfig = (priority: number) => {
  switch (priority) {
    case 1: {
      return { type: 'warning' as const, label: $t('dashboard-design.widgets.announcement.priority.important') };
    }
    case 2: {
      return { type: 'danger' as const, label: $t('dashboard-design.widgets.announcement.priority.urgent') };
    }
    default: {
      return { type: 'info' as const, label: $t('dashboard-design.widgets.announcement.priority.normal') };
    }
  }
};

// 格式化时间
const formatTime = (dateStr?: string) => {
  if (!dateStr) return '';
  // 处理 "2025-12-01 21:47:29" 格式，替换空格为T以兼容所有浏览器
  const date = new Date(dateStr.replace(' ', 'T'));
  if (isNaN(date.getTime())) return dateStr;

  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60_000);
  const hours = Math.floor(diff / 3_600_000);
  const days = Math.floor(diff / 86_400_000);

  if (minutes < 1) return $t('dashboard-design.widgets.announcement.time.justNow');
  if (minutes < 60) return `${minutes}${$t('dashboard-design.widgets.announcement.time.minutesAgo')}`;
  if (hours < 24) return `${hours}${$t('dashboard-design.widgets.announcement.time.hoursAgo')}`;
  if (days < 7) return `${days}${$t('dashboard-design.widgets.announcement.time.daysAgo')}`;
  return date.toLocaleDateString();
};

// 加载公告数据
const loadAnnouncements = async () => {
  loading.value = true;
  try {
    const limit = props.widget.props.limit || 5;
    const res = await getUserAnnouncementListApi({ page: 1, pageSize: limit });
    announcements.value = res.items || [];
  } catch (error) {
    console.error('Failed to load announcements:', error);
  } finally {
    loading.value = false;
  }
};

// 查看公告详情（会自动标记已读）
const viewDetail = async (item: UserAnnouncement) => {
  detailVisible.value = true;
  detailLoading.value = true;

  try {
    // 获取详情会自动标记已读
    const detail = await getUserAnnouncementDetailApi(item.id);
    currentAnnouncement.value = detail;
    // 更新列表中的已读状态
    item.is_read = true;
  } catch (error) {
    console.error('Failed to load announcement detail:', error);
    currentAnnouncement.value = item;
  } finally {
    detailLoading.value = false;
  }
};

// 全部已读（逐个标记）
const markAllRead = async () => {
  if (unreadCount.value === 0) return;

  const unreadItems = announcements.value.filter((a) => !a.is_read);
  for (const item of unreadItems) {
    try {
      await getUserAnnouncementDetailApi(item.id);
      item.is_read = true;
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  }
};

onMounted(() => {
  loadAnnouncements();
});
</script>

<template>
  <div class="announcement-list flex h-full flex-col p-3">
    <div class="mb-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Megaphone class="text-muted-foreground h-4 w-4" />
        <span class="text-muted-foreground text-sm font-medium">{{
          widget.props.title
        }}</span>
        <ElTag v-if="unreadCount > 0" type="danger" size="small" round>
          {{ unreadCount }}
        </ElTag>
      </div>
      <ElButton
        v-if="unreadCount > 0"
        type="primary"
        text
        size="small"
        @click="markAllRead"
      >
        <CheckCheck class="mr-1 h-3.5 w-3.5" />
        {{ $t('dashboard-design.widgets.announcement.markAllRead') }}
      </ElButton>
    </div>
    <ElScrollbar class="flex-1">
      <div v-if="announcements.length > 0" class="space-y-2">
        <div
          v-for="item in announcements"
          :key="item.id"
          class="cursor-pointer rounded-md p-2 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
          :class="{ 'opacity-60': item.is_read }"
          @click="viewDetail(item)"
        >
          <div class="flex items-start gap-2">
            <ElTag
              v-if="item.is_top"
              type="danger"
              size="small"
              effect="dark"
              class="flex-shrink-0"
            >
              {{ $t('dashboard-design.widgets.announcement.top') }}
            </ElTag>
            <ElTag
              :type="getPriorityConfig(item.priority).type"
              size="small"
              class="flex-shrink-0"
            >
              {{ getPriorityConfig(item.priority).label }}
            </ElTag>
            <div class="min-w-0 flex-1">
              <div class="truncate text-sm font-medium">{{ item.title }}</div>
            </div>
          </div>
          <div
            v-if="item.summary"
            class="text-muted-foreground mt-1 line-clamp-2 text-xs"
          >
            {{ item.summary }}
          </div>
          <div
            class="text-muted-foreground mt-1 flex items-center justify-between text-xs"
          >
            <span>{{ item.publisher_name }}</span>
            <span>{{ formatTime(item.publish_time) }}</span>
          </div>
        </div>
      </div>
      <ElEmpty v-else :description="$t('dashboard-design.widgets.announcement.noData')" :image-size="60" />
    </ElScrollbar>

    <!-- 公告详情弹窗 -->
    <ZqDialog
      v-model="detailVisible"
      :title="currentAnnouncement?.title"
      width="600px"
      destroy-on-close
      append-to-body
    >
      <div v-if="detailLoading" class="py-8 text-center text-gray-400">
        {{ $t('dashboard-design.widgets.announcement.loading') }}
      </div>
      <div v-else-if="currentAnnouncement" class="space-y-4">
        <div class="flex items-center gap-2">
          <ElTag
            v-if="currentAnnouncement.is_top"
            type="danger"
            size="small"
            effect="dark"
          >
            {{ $t('dashboard-design.widgets.announcement.top') }}
          </ElTag>
          <ElTag
            :type="getPriorityConfig(currentAnnouncement.priority).type"
            size="small"
          >
            {{ getPriorityConfig(currentAnnouncement.priority).label }}
          </ElTag>
          <span class="text-muted-foreground text-xs">{{
            formatTime(currentAnnouncement.publish_time)
          }}</span>
        </div>
        <div
          class="whitespace-pre-wrap text-sm leading-relaxed"
          v-html="currentAnnouncement.content || $t('dashboard-design.widgets.announcement.noContent')"
        ></div>
        <div class="text-muted-foreground text-xs">
          {{ $t('dashboard-design.widgets.announcement.publisher') }}{{ currentAnnouncement.publisher_name }}
        </div>
      </div>
    </ZqDialog>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
