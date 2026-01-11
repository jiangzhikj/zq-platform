<script lang="ts" setup>
import type { DataSource } from '#/api/core/data-source';

import { computed, ref, watch } from 'vue';

import { $t } from '@vben/locales';
import { Play } from '@vben/icons';

import {
  ElButton,
  ElCard,
  ElCol,
  ElDialog,
  ElForm,
  ElFormItem,
  ElInput,
  ElMessage,
  ElRow,
  ElScrollbar,
  ElTag,
} from 'element-plus';

import { previewDataSourceApi } from '#/api/core/data-source';

interface Props {
  modelValue: boolean;
  dataSource: DataSource;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

const loading = ref(false);
const testParams = ref<Record<string, any>>({});
const testResult = ref<null | {
  data: any[];
  limited: number;
  total: number;
}>(null);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

// 监听弹窗打开，初始化参数
watch(
  () => props.modelValue,
  (visible) => {
    if (visible) {
      testResult.value = null;
      initTestParams();
    }
  },
);

/**
 * 初始化测试参数默认值
 */
function initTestParams() {
  testParams.value = {};
  if (props.dataSource.params && props.dataSource.params.length > 0) {
    for (const param of props.dataSource.params) {
      if (param.default !== undefined && param.default !== null) {
        testParams.value[param.name] = param.default;
      }
    }
  }
}

/**
 * 执行测试
 */
async function handleTest() {
  loading.value = true;
  testResult.value = null;

  try {
    const result = await previewDataSourceApi(props.dataSource.id, {
      params: testParams.value,
      limit: 100,
    });

    testResult.value = result;
    ElMessage.success($t('data-source.testConnectionSuccess'));
  } catch (error: any) {
    ElMessage.error(error?.message || $t('data-source.testDataSourceFailed'));
  } finally {
    loading.value = false;
  }
}

function handleClose() {
  dialogVisible.value = false;
}
</script>

<template>
  <ElDialog
    v-model="dialogVisible"
    :title="`${$t('data-source.testDataSource')}: ${dataSource.name}`"
    width="700px"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div class="space-y-4">
      <!-- 数据源信息 -->
      <ElCard shadow="never">
        <template #header>
          <span class="text-sm font-medium">{{ $t('data-source.dataSourceInfo') }}</span>
        </template>
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="text-muted-foreground">{{ $t('data-source.code') }}:</span>
            <span class="font-mono">{{ dataSource.code }}</span>
          </div>
          <div>
            <span class="text-muted-foreground">{{ $t('data-source.type') }}:</span>
            <ElTag size="small">
              {{ dataSource.source_type.toUpperCase() }}
            </ElTag>
          </div>
        </div>
      </ElCard>

      <!-- 测试参数 -->
      <ElCard
        v-if="dataSource.params && dataSource.params.length > 0"
        shadow="never"
      >
        <template #header>
          <span class="text-sm font-medium">{{ $t('data-source.testParams') }}</span>
        </template>
        <ElForm label-width="100px">
          <ElRow :gutter="16">
            <ElCol
              v-for="param in dataSource.params"
              :key="param.name"
              :span="12"
            >
              <ElFormItem :label="param.label || param.name">
                <ElInput
                  v-model="testParams[param.name]"
                  :placeholder="
                    param.default !== null ? String(param.default) : ''
                  "
                />
              </ElFormItem>
            </ElCol>
          </ElRow>
        </ElForm>
      </ElCard>

      <!-- 测试按钮 -->
      <div class="flex justify-center">
        <ElButton
          type="primary"
          :icon="Play"
          :loading="loading"
          @click="handleTest"
        >
          {{ $t('data-source.executeTest') }}
        </ElButton>
      </div>

      <!-- 测试结果 -->
      <ElCard v-if="testResult" shadow="never">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium">{{ $t('data-source.testResult') }}</span>
            <ElTag type="success" size="small">
              {{ $t('data-source.returnedData', { count: testResult.total }) }}
            </ElTag>
          </div>
        </template>
        <ElScrollbar max-height="300px">
          <pre class="bg-muted rounded p-3 text-xs">{{
            JSON.stringify(testResult.data, null, 2)
          }}</pre>
        </ElScrollbar>
      </ElCard>
    </div>

    <template #footer>
      <ElButton @click="handleClose">{{ $t('data-source.close') }}</ElButton>
    </template>
  </ElDialog>
</template>
