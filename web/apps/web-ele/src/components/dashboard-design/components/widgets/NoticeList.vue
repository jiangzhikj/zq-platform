<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import type { Message } from '#/api/core/message';

import { computed, onMounted, ref } from 'vue';

import { Bell, CheckCheck } from '@vben/icons';
import { $t } from '@vben/locales';

import { ElButton, ElDialog, ElEmpty, ElScrollbar, ElTag } from 'element-plus';

import {
  getMessageListApi,
  markAllAsReadApi,
  markAsReadApi,
} from '#/api/core/message';

const props = defineProps<{
  widget: DashboardWidget;
}>();

// 实际消息数据
const messages = ref<Message[]>([]);
const loading = ref(false);

// 详情弹窗
const detailVisible = ref(false);
const currentMessage = ref<Message | null>(null);

// 未读数量
const unreadCount = computed(
  () => messages.value.filter((m) => m.status === 'unread').length,
);

// 获取消息类型配置
const getTypeConfig = (type: string) => {
  switch (type) {
    case 'announcement': {
      return { type: 'success' as const, label: $t('message.typeMap.announcement') };
    }
    case 'system': {
      return { type: 'info' as const, label: $t('message.typeMap.system') };
    }
    case 'todo': {
      return { type: 'warning' as const, label: $t('message.typeMap.todo') };
    }
    case 'workflow': {
      return { type: 'primary' as const, label: $t('message.typeMap.workflow') };
    }
    default: {
      return { type: 'info' as const, label: $t('message.type') };
    }
  }
};

// 格式化时间
const formatTime = (dateStr: string) => {
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

// 加载消息数据
const loadMessages = async () => {
  loading.value = true;
  try {
    const limit = props.widget.props.limit || 5;
    const res = await getMessageListApi({ page: 1, pageSize: limit });
    messages.value = res.items || [];
  } catch (error) {
    console.error('Failed to load messages:', error);
  } finally {
    loading.value = false;
  }
};

// 查看消息详情
const viewDetail = async (msg: Message) => {
  currentMessage.value = msg;
  detailVisible.value = true;

  // 标记为已读
  if (msg.status === 'unread') {
    try {
      await markAsReadApi(msg.id);
      msg.status = 'read';
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  }
};

// 全部已读
const markAllRead = async () => {
  if (unreadCount.value === 0) return;

  try {
    await markAllAsReadApi();
    messages.value.forEach((msg) => {
      msg.status = 'read';
    });
  } catch (error) {
    console.error('Failed to mark all as read:', error);
  }
};

onMounted(() => {
  loadMessages();
});
</script>

<template>
  <div class="notice-list flex h-full flex-col p-3">
    <div class="mb-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Bell class="text-muted-foreground h-4 w-4" />
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
      <div v-if="messages.length > 0" class="space-y-2">
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="flex cursor-pointer items-start gap-2 rounded-md p-2 transition-colors hover:bg-gray-50 dark:hover:bg-gray-800"
          :class="{ 'opacity-60': msg.status === 'read' }"
          @click="viewDetail(msg)"
        >
          <ElTag
            :type="getTypeConfig(msg.msg_type).type"
            size="small"
            class="flex-shrink-0"
          >
            {{ getTypeConfig(msg.msg_type).label }}
          </ElTag>
          <div class="min-w-0 flex-1">
            <div class="truncate text-sm">{{ msg.title }}</div>
            <div class="text-muted-foreground mt-1 flex items-center text-xs">
              <span v-if="msg.content" class="flex-1 truncate">{{
                msg.content
              }}</span>
              <span class="ml-2 flex-shrink-0">{{
                formatTime(msg.created_at)
              }}</span>
            </div>
          </div>
        </div>
      </div>
      <ElEmpty v-else :description="$t('message.noData') || $t('dashboard-design.widgets.announcement.noData')" :image-size="60" />
    </ElScrollbar>

    <!-- 消息详情弹窗 -->
    <ElDialog
      v-model="detailVisible"
      :title="currentMessage?.title"
      width="500px"
      destroy-on-close
      append-to-body
    >
      <div v-if="currentMessage" class="space-y-4">
        <div class="flex items-center gap-2">
          <ElTag
            :type="getTypeConfig(currentMessage.msg_type).type"
            size="small"
          >
            {{ getTypeConfig(currentMessage.msg_type).label }}
          </ElTag>
          <span class="text-muted-foreground text-xs">{{
            formatTime(currentMessage.created_at)
          }}</span>
        </div>
        <div class="whitespace-pre-wrap text-sm leading-relaxed">
          {{ currentMessage.content || $t('dashboard-design.widgets.announcement.noContent') }}
        </div>
        <div
          v-if="currentMessage.sender_name"
          class="text-muted-foreground text-xs"
        >
          {{ $t('message.sender') || '发送者：' }}{{ currentMessage.sender_name }}
        </div>
      </div>
    </ElDialog>
  </div>
</template>

<style scoped>
/* 背景色由 WidgetRenderer 控制 */
</style>
