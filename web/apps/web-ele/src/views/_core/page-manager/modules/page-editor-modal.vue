<script lang="ts" setup>
import { computed, ref, watch } from 'vue';

import { $t } from '@vben/locales';

import {
  ElButton,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElOption,
  ElSelect,
} from 'element-plus';

import {
  createPageApi,
  getPageDetailApi,
  updatePageApi,
} from '#/api/core/page-manager';
import DashboardDesign from '#/components/dashboard-design/index.vue';
import { useDashboardDesignStore } from '#/components/dashboard-design/store/dashboardDesignStore';

interface Props {
  modelValue: boolean;
  pageId?: null | string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  save: [];
  'update:modelValue': [value: boolean];
}>();

const dashboardDesignStore = useDashboardDesignStore();
const loading = ref(false);
const isEditMode = computed(() => !!props.pageId);

// 当前步骤
const currentStep = ref(0);

// 基础信息表单
const basicForm = ref({
  name: '',
  code: '',
  category: '',
  sort: 0,
  description: '',
});

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const steps = [
  { title: $t('page-manager.editor.steps.basic'), index: 1 },
  { title: $t('page-manager.editor.steps.design'), index: 2 },
];

const canGoNext = computed(() => {
  if (currentStep.value === 0) {
    return basicForm.value.name && basicForm.value.code;
  }
  return true;
});

// 监听弹窗打开，编辑模式下加载数据
watch(
  () => props.modelValue,
  async (visible) => {
    if (visible && props.pageId) {
      await loadPageData(props.pageId);
    }
  },
);

// 加载页面数据
async function loadPageData(pageId: string) {
  loading.value = true;
  try {
    const page = await getPageDetailApi(pageId);

    // 恢复基础信息
    basicForm.value = {
      name: page.name,
      code: page.code,
      category: page.category,
      description: page.description,
      sort: page.sort,
    };

    // 恢复页面设计配置
    if (page.page_config && Object.keys(page.page_config).length > 0) {
      dashboardDesignStore.importConfig(JSON.stringify(page.page_config));
    }
  } catch (error: any) {
    ElMessage.error(error?.message || $t('page-manager.editor.loadFailed'));
  } finally {
    loading.value = false;
  }
}

const canGoPrev = computed(() => currentStep.value > 0);

const isLastStep = computed(() => currentStep.value === steps.length - 1);

function handleNext() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
  }
}

function handlePrev() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

async function handleSave() {
  loading.value = true;
  try {
    // 获取页面设计配置
    const pageConfig = JSON.parse(dashboardDesignStore.exportConfig());

    const pageData = {
      name: basicForm.value.name,
      code: basicForm.value.code,
      category: basicForm.value.category,
      description: basicForm.value.description,
      sort: basicForm.value.sort,
      page_config: pageConfig,
    };

    await (isEditMode.value && props.pageId
      ? updatePageApi(props.pageId, pageData)
      : createPageApi(pageData));

    emit('save');
    handleClose();
  } catch (error: any) {
    ElMessage.error(error?.message || $t('common.saveFailed'));
  } finally {
    loading.value = false;
  }
}

function handleClose() {
  dialogVisible.value = false;
  // 重置状态
  currentStep.value = 0;
  basicForm.value = {
    name: '',
    code: '',
    category: '',
    sort: 0,
    description: '',
  };
  // 清空页面设计
  dashboardDesignStore.clearCanvas();
  dashboardDesignStore.setActive(null);
}

// 处理设计器保存事件
function handleDesignSave(_config: string) {
  // 设计器内部保存，这里可以做一些额外处理
  // 配置已经在 store 中，保存时会自动获取
}
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    :show-close="false"
    fullscreen
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    body-class="h-[calc(100vh-106px)]"
    header-class="!pb-0"
  >
    <template #header>
      <div
        class="bg-background-deep mb-4 flex h-14 w-full items-center justify-between rounded-[8px] px-6 shadow-sm"
      >
        <!-- 左侧：Logo和标题 -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <div
              class="bg-primary flex h-8 w-8 items-center justify-center rounded"
            >
              <span class="text-sm font-bold text-white">P</span>
            </div>
            <span class="text-foreground/70 text-base font-medium"
              >{{ $t('page-manager.editor.title') }}</span
            >
          </div>
        </div>

        <!-- 中间：步骤条 -->
        <div class="absolute left-1/2 flex -translate-x-1/2 items-center">
          <template v-for="(step, index) in steps" :key="index">
            <div
              class="flex cursor-pointer items-center px-4 py-1"
              @click="index < currentStep ? (currentStep = index) : null"
            >
              <div
                class="flex items-center justify-center rounded-full border px-3 py-1 text-sm transition-all"
                :class="[
                  index === currentStep
                    ? 'border-primary text-primary bg-primary/10 font-medium'
                    : index < currentStep
                      ? 'border-primary/50 text-primary/80 bg-transparent'
                      : 'border-border text-muted-foreground bg-transparent',
                ]"
              >
                <span
                  class="mr-2 flex h-5 w-5 items-center justify-center rounded-full text-xs"
                  :class="
                    index === currentStep
                      ? 'bg-primary text-white'
                      : index < currentStep
                        ? 'bg-primary/80 text-white'
                        : 'bg-muted text-muted-foreground'
                  "
                >
                  {{ step.index }}
                </span>
                {{ step.title }}
              </div>
            </div>
            <div
              v-if="index < steps.length - 1"
              class="bg-border h-[1px] w-8"
              :class="{ 'bg-primary/50': index < currentStep }"
            ></div>
          </template>
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="flex items-center gap-3">
          <ElButton v-if="canGoPrev" @click="handlePrev"> {{ $t('common.prev') }} </ElButton>
          <ElButton
            v-if="!isLastStep"
            type="primary"
            :disabled="!canGoNext"
            @click="handleNext"
          >
            {{ $t('common.next') }}
          </ElButton>
          <ElButton
            v-if="isLastStep"
            type="primary"
            :loading="loading"
            @click="handleSave"
          >
            {{ $t('common.save') }}
          </ElButton>
          <ElButton @click="handleClose"> {{ $t('common.close') }} </ElButton>
        </div>
      </div>
    </template>

    <!-- 步骤内容 -->
    <div class="h-full overflow-hidden">
      <!-- 步骤1: 基础信息 -->
      <div
        v-show="currentStep === 0"
        class="flex h-full items-center justify-center overflow-y-auto"
      >
        <div class="align-self-center w-[600px] translate-y-[-20%]">
          <div class="border-border bg-card rounded-lg border p-8 shadow-sm">
            <h3 class="mb-6 text-center text-lg font-medium">{{ $t('page-manager.editor.steps.basic') }}</h3>
            <ElForm
              :model="basicForm"
              label-width="100px"
              label-position="right"
              class="form-content"
            >
              <ElFormItem :label="$t('page-manager.name')" required>
                <ElInput
                  v-model="basicForm.name"
                  :placeholder="$t('page-manager.placeholder.name')"
                  clearable
                />
              </ElFormItem>
              <ElFormItem :label="$t('page-manager.code')" required>
                <ElInput
                  v-model="basicForm.code"
                  :placeholder="$t('page-manager.placeholder.code')"
                  clearable
                  :disabled="isEditMode"
                />
              </ElFormItem>
              <ElFormItem :label="$t('page-manager.category')">
                <ElSelect
                  v-model="basicForm.category"
                  :placeholder="$t('page-manager.placeholder.category')"
                  class="w-full"
                  clearable
                >
                  <ElOption :label="$t('page-manager.categoryMap.dashboard')" value="dashboard" />
                  <ElOption :label="$t('page-manager.categoryMap.portal')" value="portal" />
                  <ElOption :label="$t('page-manager.categoryMap.databoard')" value="databoard" />
                  <ElOption :label="$t('page-manager.categoryMap.other')" value="other" />
                </ElSelect>
              </ElFormItem>
              <ElFormItem :label="$t('common.sort')">
                <ElInput
                  v-model.number="basicForm.sort"
                  type="number"
                  placeholder="0"
                />
              </ElFormItem>
              <ElFormItem :label="$t('page-manager.description')">
                <ElInput
                  v-model="basicForm.description"
                  type="textarea"
                  :rows="4"
                  :placeholder="$t('page-manager.placeholder.description')"
                />
              </ElFormItem>
            </ElForm>
          </div>
        </div>
      </div>

      <!-- 步骤2: 页面设计 -->
      <div v-show="currentStep === 1" class="h-full overflow-hidden">
        <DashboardDesign @save="handleDesignSave" />
      </div>
    </div>
  </ElDialog>
</template>
