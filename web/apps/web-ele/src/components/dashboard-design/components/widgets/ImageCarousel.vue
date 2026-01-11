<script setup lang="ts">
import type { DashboardWidget } from '../../store/dashboardDesignStore';

import { computed, onMounted, onUnmounted, ref, watch } from 'vue';

import { ChevronLeft, ChevronRight } from '@vben/icons';
import { $t } from '@vben/locales';

import { getFileStreamUrl } from '#/api/core/file';

const props = defineProps<{
  isDesignMode?: boolean;
  widget: DashboardWidget;
}>();

const currentIndex = ref(0);
let autoplayTimer: null | ReturnType<typeof setInterval> = null;

// 解析图片URL，支持 file:// 前缀的文件ID
const resolveImageUrl = (url: string): string => {
  if (!url) return '';
  if (url.startsWith('file://')) {
    const fileId = url.slice(7);
    return getFileStreamUrl(fileId);
  }
  return url;
};

// 处理后的图片列表
const images = computed(() => {
  const rawImages = props.widget.props.images || [];
  return rawImages.map((img: any) => ({
    ...img,
    url: resolveImageUrl(img.url || ''),
  }));
});

const nextSlide = () => {
  if (images.value.length === 0) return;
  currentIndex.value = (currentIndex.value + 1) % images.value.length;
};

const prevSlide = () => {
  if (images.value.length === 0) return;
  currentIndex.value =
    (currentIndex.value - 1 + images.value.length) % images.value.length;
};

const goToSlide = (index: number) => {
  currentIndex.value = index;
};

const startAutoplay = () => {
  if (autoplayTimer) {
    clearInterval(autoplayTimer);
  }
  if (props.widget.props.autoplay && !props.isDesignMode) {
    const interval = props.widget.props.interval || 3000;
    autoplayTimer = setInterval(nextSlide, interval);
  }
};

const stopAutoplay = () => {
  if (autoplayTimer) {
    clearInterval(autoplayTimer);
    autoplayTimer = null;
  }
};

const handleImageClick = (image: any) => {
  if (image.link && !props.isDesignMode) {
    window.open(image.link, '_blank');
  }
};

onMounted(() => {
  startAutoplay();
});

onUnmounted(() => {
  stopAutoplay();
});

watch(
  () => props.widget.props.autoplay,
  () => {
    if (props.widget.props.autoplay) {
      startAutoplay();
    } else {
      stopAutoplay();
    }
  },
);
</script>

<template>
  <div
    class="image-carousel relative h-full w-full overflow-hidden"
    @mouseenter="stopAutoplay"
    @mouseleave="startAutoplay"
  >
    <!-- 图片容器 -->
    <div
      class="carousel-track flex h-full transition-transform duration-500 ease-in-out"
      :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
    >
      <div
        v-for="(image, index) in images"
        :key="index"
        class="carousel-slide h-full w-full flex-shrink-0"
        :class="{ 'cursor-pointer': image.link && !isDesignMode }"
        @click="handleImageClick(image)"
      >
        <img
          :src="image.url"
          :alt="image.title || `${$t('dashboard-design.widgets.image.title')} ${Number(index) + 1}`"
          class="h-full w-full object-cover"
        />
        <div v-if="image.title" class="slide-title">
          {{ image.title }}
        </div>
      </div>
    </div>

    <!-- 左右箭头 -->
    <template v-if="widget.props.showArrow && images.length > 1">
      <button class="arrow-btn arrow-left" @click.stop="prevSlide">
        <ChevronLeft class="h-5 w-5" />
      </button>
      <button class="arrow-btn arrow-right" @click.stop="nextSlide">
        <ChevronRight class="h-5 w-5" />
      </button>
    </template>

    <!-- 指示器 -->
    <div
      v-if="widget.props.showIndicator && images.length > 1"
      class="indicators"
    >
      <button
        v-for="(_, index) in images"
        :key="index"
        class="indicator"
        :class="{ active: currentIndex === Number(index) }"
        @click.stop="goToSlide(Number(index))"
      ></button>
    </div>

    <!-- 空状态 -->
    <div
      v-if="images.length === 0"
      class="flex h-full w-full items-center justify-center text-gray-400"
    >
      {{ $t('dashboard-design.widgets.image.noData') }}
    </div>
  </div>
</template>

<style scoped>
.carousel-track {
  will-change: transform;
}

.slide-title {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  padding: 8px 12px;
  font-size: 0.875rem;
  color: white;
  background: linear-gradient(transparent, rgb(0 0 0 / 60%));
}

.arrow-btn {
  position: absolute;
  top: 50%;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  cursor: pointer;
  background: rgb(255 255 255 / 80%);
  border: none;
  border-radius: 50%;
  opacity: 0;
  transform: translateY(-50%);
  transition: opacity 0.2s;
}

.image-carousel:hover .arrow-btn {
  opacity: 1;
}

.arrow-btn:hover {
  background: rgb(255 255 255 / 100%);
}

.arrow-left {
  left: 8px;
}

.arrow-right {
  right: 8px;
}

.indicators {
  position: absolute;
  bottom: 12px;
  left: 50%;
  z-index: 10;
  display: flex;
  gap: 6px;
  transform: translateX(-50%);
}

.indicator {
  width: 8px;
  height: 8px;
  cursor: pointer;
  background: rgb(255 255 255 / 50%);
  border: none;
  border-radius: 50%;
  transition: all 0.2s;
}

.indicator.active {
  width: 20px;
  background: white;
  border-radius: 4px;
}
</style>
