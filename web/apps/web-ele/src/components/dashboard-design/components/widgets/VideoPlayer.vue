<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed, onMounted, ref, watch } from 'vue';

import { Maximize, Pause, Play, Volume2, VolumeX } from '@vben/icons';

import { $t } from '@vben/locales';

import { getFileStreamUrl } from '#/api/core/file';

const props = defineProps<{
  isDesignMode?: boolean;
  widget: DashboardWidget;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref(false);
const isMuted = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const progress = ref(0);

// 解析URL，支持 file:// 前缀的文件ID
const resolveUrl = (url: string): string => {
  if (!url) return '';
  if (url.startsWith('file://')) {
    const fileId = url.slice(7);
    return getFileStreamUrl(fileId);
  }
  return url;
};

const videoUrl = computed(() => resolveUrl(props.widget.props.url || ''));
const posterUrl = computed(() => resolveUrl(props.widget.props.poster || ''));

const togglePlay = () => {
  if (!videoRef.value) return;

  if (isPlaying.value) {
    videoRef.value.pause();
  } else {
    videoRef.value.play();
  }
};

const toggleMute = () => {
  if (!videoRef.value) return;
  videoRef.value.muted = !videoRef.value.muted;
  isMuted.value = videoRef.value.muted;
};

const toggleFullscreen = () => {
  if (!videoRef.value) return;

  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    videoRef.value.requestFullscreen();
  }
};

const handleTimeUpdate = () => {
  if (!videoRef.value) return;
  currentTime.value = videoRef.value.currentTime;
  progress.value = (currentTime.value / duration.value) * 100;
};

const handleLoadedMetadata = () => {
  if (!videoRef.value) return;
  duration.value = videoRef.value.duration;
};

const handlePlay = () => {
  isPlaying.value = true;
};

const handlePause = () => {
  isPlaying.value = false;
};

const handleSeek = (e: MouseEvent) => {
  if (!videoRef.value) return;
  const target = e.currentTarget as HTMLElement;
  const rect = target.getBoundingClientRect();
  const percent = (e.clientX - rect.left) / rect.width;
  videoRef.value.currentTime = percent * duration.value;
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

onMounted(() => {
  if (videoRef.value) {
    isMuted.value = props.widget.props.muted || false;
    videoRef.value.muted = isMuted.value;
  }
});

watch(
  () => props.widget.props.url,
  () => {
    if (videoRef.value) {
      videoRef.value.load();
      isPlaying.value = false;
      currentTime.value = 0;
      progress.value = 0;
    }
  },
);
</script>

<template>
  <div class="video-player flex h-full flex-col">
    <div
      v-if="widget.props.title"
      class="text-muted-foreground p-2 text-sm font-medium"
    >
      {{ widget.props.title }}
    </div>

    <div class="video-container relative min-h-0 flex-1 bg-black">
      <video
        ref="videoRef"
        :src="videoUrl"
        :poster="posterUrl"
        :autoplay="widget.props.autoplay && !isDesignMode"
        :loop="widget.props.loop"
        :controls="false"
        class="h-full w-full object-contain"
        @timeupdate="handleTimeUpdate"
        @loadedmetadata="handleLoadedMetadata"
        @play="handlePlay"
        @pause="handlePause"
      ></video>

      <!-- 自定义控制栏 -->
      <div v-if="!widget.props.controls" class="custom-controls">
        <button class="control-btn" @click="togglePlay">
          <Play v-if="!isPlaying" class="h-5 w-5" />
          <Pause v-else class="h-5 w-5" />
        </button>

        <div class="progress-bar" @click="handleSeek">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>

        <span class="time-display">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </span>

        <button class="control-btn" @click="toggleMute">
          <VolumeX v-if="isMuted" class="h-4 w-4" />
          <Volume2 v-else class="h-4 w-4" />
        </button>

        <button class="control-btn" @click="toggleFullscreen">
          <Maximize class="h-4 w-4" />
        </button>
      </div>

      <!-- 原生控制栏 -->
      <video
        v-if="widget.props.controls"
        ref="videoRef"
        :src="videoUrl"
        :poster="posterUrl"
        :autoplay="widget.props.autoplay && !isDesignMode"
        :loop="widget.props.loop"
        :muted="widget.props.muted"
        controls
        class="h-full w-full object-contain"
      ></video>

      <!-- 设计模式遮罩 -->
      <div v-if="isDesignMode" class="design-overlay">
        <Play class="h-12 w-12 text-white/80" />
        <div class="mt-2 text-sm text-white/80">{{ $t('dashboard-design.widgets.video.placeholder') }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.video-container {
  position: relative;
  overflow: hidden;
}

.custom-controls {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 8px 12px;
  background: linear-gradient(transparent, rgb(0 0 0 / 70%));
  opacity: 0;
  transition: opacity 0.2s;
}

.video-container:hover .custom-controls {
  opacity: 1;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: white;
  cursor: pointer;
  background: transparent;
  border: none;
  border-radius: 4px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgb(255 255 255 / 20%);
}

.progress-bar {
  flex: 1;
  height: 4px;
  overflow: hidden;
  cursor: pointer;
  background: rgb(255 255 255 / 30%);
  border-radius: 2px;
}

.progress-fill {
  height: 100%;
  background: var(--el-color-primary);
  transition: width 0.1s;
}

.time-display {
  min-width: 80px;
  font-size: 12px;
  color: white;
  text-align: center;
}

.design-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgb(0 0 0 / 50%);
}
</style>
