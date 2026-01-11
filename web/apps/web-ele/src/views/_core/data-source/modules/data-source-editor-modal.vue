<script lang="ts" setup>
import type { DataSource } from '#/api/core/data-source';

import { computed, reactive, ref, watch } from 'vue';

import { $t } from '@vben/locales';
import { CirclePlus, Play, Settings, Trash } from '@vben/icons';

import {
  ElAlert,
  ElButton,
  ElCard,
  ElCol,
  ElDialog,
  ElDivider,
  ElForm,
  ElFormItem,
  ElInput,
  ElInputNumber,
  ElMessage,
  ElOption,
  ElRadioButton,
  ElRadioGroup,
  ElRow,
  ElScrollbar,
  ElSelect,
  ElSplitter,
  ElSplitterPanel,
  ElSwitch,
  ElTable,
  ElTableColumn,
  ElTabPane,
  ElTabs,
  ElTag,
  ElTooltip,
} from 'element-plus';

import {
  createDataSourceApi,
  getDataSourceDetailApi,
  testDataSourceApi,
  updateDataSourceApi,
} from '#/api/core/data-source';

import {
  defaultDataSource,
  getParamTypeOptions,
  getResultTypeOptions,
  getSourceTypeOptions,
  httpMethodOptions,
} from '../data';
import DbSchemaPanel from './db-schema-panel.vue';

interface Props {
  modelValue: boolean;
  dataSourceId?: null | string;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  save: [];
  'update:modelValue': [value: boolean];
}>();

const loading = ref(false);
const currentStep = ref(0);

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const isEditMode = computed(() => !!props.dataSourceId);

// 步骤定义
const steps = [
  { title: $t('data-source.basicInfo'), index: 1 },
  { title: $t('data-source.dataSourceConfig'), index: 2 },
];

// 表单数据
const formData = reactive<DataSource>({
  ...defaultDataSource,
} as DataSource);

// 测试相关
const testLoading = ref(false);
const testParams = ref<Record<string, any>>({});
const testResult = ref<null | {
  data: any[];
  limited: number;
  success: boolean;
  total: number;
}>(null);
const configActiveTab = ref('params');

// SQL 编辑器引用
const sqlEditorRef = ref<HTMLTextAreaElement>();

// 当前选中的数据库上下文
const dbContext = ref<null | {
  database?: string;
  dbName: string;
  schema?: string;
}>(null);

// 数据库上下文显示文本
const dbContextDisplay = computed(() => {
  if (!dbContext.value) return $t('data-source.noData');
  const parts = [dbContext.value.dbName];
  if (dbContext.value.database) parts.push(dbContext.value.database);
  if (dbContext.value.schema) parts.push(dbContext.value.schema);
  return parts.join(' / ');
});

// JSON 字符串编辑（用于 textarea）
const apiHeadersStr = computed({
  get: () => JSON.stringify(formData.api_headers || {}, null, 2),
  set: (v: string) => {
    try {
      formData.api_headers = JSON.parse(v);
    } catch {
      // 忽略解析错误
    }
  },
});

const apiBodyStr = computed({
  get: () => JSON.stringify(formData.api_body || {}, null, 2),
  set: (v: string) => {
    try {
      formData.api_body = JSON.parse(v);
    } catch {
      // 忽略解析错误
    }
  },
});

const staticDataStr = computed({
  get: () => JSON.stringify(formData.static_data || [], null, 2),
  set: (v: string) => {
    try {
      formData.static_data = JSON.parse(v);
    } catch {
      // 忽略解析错误
    }
  },
});

// 图表配置 - 系列字段（逗号分隔字符串）
const chartSeriesFieldsStr = computed({
  get: () => (formData.chart_config?.series_fields || []).join(', '),
  set: (v: string) => {
    if (!formData.chart_config) formData.chart_config = {};
    formData.chart_config.series_fields = v
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

// 图表配置 - 系列名称（逗号分隔字符串）
const chartSeriesNamesStr = computed({
  get: () => (formData.chart_config?.series_names || []).join(', '),
  set: (v: string) => {
    if (!formData.chart_config) formData.chart_config = {};
    formData.chart_config.series_names = v
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

// 图表配置 - 数值字段（雷达图用，逗号分隔字符串）
const chartValueFieldsStr = computed({
  get: () => (formData.chart_config?.value_fields || []).join(', '),
  set: (v: string) => {
    if (!formData.chart_config) formData.chart_config = {};
    formData.chart_config.value_fields = v
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  },
});

// 标题
const title = computed(() => (isEditMode.value ? $t('data-source.editDataSource') : $t('data-source.createDataSource')));

// 选项列表（国际化）
const sourceTypeOptions = computed(() => getSourceTypeOptions());
const resultTypeOptions = computed(() => getResultTypeOptions());
const paramTypeOptions = computed(() => getParamTypeOptions());

// 步骤验证
const canGoNext = computed(() => {
  if (currentStep.value === 0) {
    return formData.name && formData.code && formData.source_type;
  }
  return true;
});

const canGoPrev = computed(() => currentStep.value > 0);
const isLastStep = computed(() => currentStep.value === steps.length - 1);

// 监听弹窗打开，加载数据
watch(
  () => props.modelValue,
  async (visible) => {
    if (visible) {
      currentStep.value = 0;
      testResult.value = null;
      testParams.value = {};
      configActiveTab.value = 'params';
      Object.assign(formData, defaultDataSource);

      if (props.dataSourceId) {
        loading.value = true;
        try {
          const data = await getDataSourceDetailApi(props.dataSourceId);
          Object.assign(formData, data);
          initTestParams();
        } catch {
          ElMessage.error($t('data-source.loadDataSourceFailed'));
          dialogVisible.value = false;
        } finally {
          loading.value = false;
        }
      }
    }
  },
);

/**
 * 初始化测试参数默认值
 */
function initTestParams() {
  testParams.value = {};
  if (formData.params && formData.params.length > 0) {
    for (const param of formData.params) {
      if (param.default !== undefined && param.default !== null) {
        testParams.value[param.name] = param.default;
      }
    }
  }
}

/**
 * 下一步
 */
function handleNext() {
  if (currentStep.value < steps.length - 1) {
    currentStep.value++;
  }
}

/**
 * 上一步
 */
function handlePrev() {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
}

/**
 * 关闭弹窗
 */
function handleClose() {
  dialogVisible.value = false;
}

/**
 * 保存
 */
async function handleSave() {
  loading.value = true;
  try {
    if (isEditMode.value && props.dataSourceId) {
      await updateDataSourceApi(props.dataSourceId, formData);
      ElMessage.success($t('data-source.updateDataSourceSuccess'));
    } else {
      await createDataSourceApi(formData);
      ElMessage.success($t('data-source.createDataSourceSuccess'));
    }
    emit('save');
    handleClose();
  } catch (error: any) {
    ElMessage.error(error?.message || $t('data-source.error'));
  } finally {
    loading.value = false;
  }
}

/**
 * 测试数据源
 */
async function handleTest() {
  testLoading.value = true;
  testResult.value = null;

  try {
    const result = await testDataSourceApi({
      source_type: formData.source_type,
      api_url: formData.api_url,
      api_method: formData.api_method,
      api_headers: formData.api_headers,
      api_body: formData.api_body,
      api_timeout: formData.api_timeout,
      api_data_path: formData.api_data_path,
      sql_content: formData.sql_content,
      db_connection: formData.db_connection,
      static_data: formData.static_data,
      params_def: formData.params,
      params: testParams.value,
      result_type: formData.result_type,
      tree_config: formData.tree_config,
      field_mapping: formData.field_mapping,
      chart_config: formData.chart_config,
    });

    testResult.value = result;
    if (result.success) {
      ElMessage.success($t('data-source.testConnectionSuccess'));
    }
  } catch (error: any) {
    ElMessage.error(error?.message || $t('data-source.testDataSourceFailed'));
  } finally {
    testLoading.value = false;
  }
}

/**
 * 添加参数
 */
function addParam() {
  if (!formData.params) {
    formData.params = [];
  }
  formData.params.push({
    name: '',
    label: $t('data-source.paramLabel'),
    type: 'string',
    required: false,
    default: null,
  });
}

/**
 * 删除参数
 */
function removeParam(index: number) {
  formData.params?.splice(index, 1);
}

/**
 * 添加字段映射
 */
function addFieldMapping() {
  if (!formData.field_mapping) {
    formData.field_mapping = {};
  }
  const key = `field_${Object.keys(formData.field_mapping).length + 1}`;
  formData.field_mapping[key] = '';
}

/**
 * 删除字段映射
 */
function removeFieldMapping(key: string) {
  if (formData.field_mapping) {
    delete formData.field_mapping[key];
  }
}

/**
 * 更新字段映射键
 */
function updateFieldMappingKey(oldKey: string, newKey: string) {
  if (formData.field_mapping && oldKey !== newKey) {
    const value = formData.field_mapping[oldKey];
    delete formData.field_mapping[oldKey];
    formData.field_mapping[newKey] = value || '';
  }
}

/**
 * 插入表名到 SQL 编辑器
 */
function handleInsertTable(tableName: string) {
  if (formData.source_type === 'sql' && sqlEditorRef.value) {
    const textarea = sqlEditorRef.value;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = formData.sql_content || '';
    formData.sql_content =
      text.slice(0, Math.max(0, start)) +
      tableName +
      text.slice(Math.max(0, end));
    // 设置光标位置
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + tableName.length,
        start + tableName.length,
      );
    }, 0);
  }
}

/**
 * 插入字段名到 SQL 编辑器
 */
function handleInsertField(tableName: string, fieldName: string) {
  if (formData.source_type === 'sql' && sqlEditorRef.value) {
    const textarea = sqlEditorRef.value;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = formData.sql_content || '';
    const insertText = `${tableName}.${fieldName}`;
    formData.sql_content =
      text.slice(0, Math.max(0, start)) +
      insertText +
      text.slice(Math.max(0, end));
    // 设置光标位置
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + insertText.length,
        start + insertText.length,
      );
    }, 0);
  }
}

/**
 * 处理数据库上下文选择
 */
function handleSelectContext(context: {
  database?: string;
  dbName: string;
  schema?: string;
}) {
  dbContext.value = context;
  // 更新 formData 的数据库连接
  formData.db_connection = context.dbName;
}

/**
 * 快速测试（在配置区直接测试）
 */
async function handleQuickTest() {
  // 切换到测试 Tab 并执行测试
  configActiveTab.value = 'test';
  await handleTest();
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
        class="bg-background-deep flex h-14 w-full items-center justify-between rounded-lg px-6 shadow-sm"
      >
        <!-- 左侧：Logo和标题 -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2">
            <div
              class="bg-primary flex h-8 w-8 items-center justify-center rounded"
            >
              <span class="text-sm font-bold text-white">D</span>
            </div>
            <span class="text-foreground/70 text-base font-medium">{{
              title
            }}</span>
            <ElTag v-if="formData.code" size="small" type="info">
              {{ formData.code }}
            </ElTag>
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
                    ? 'border-primary bg-primary/10 text-primary font-medium'
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
          <ElButton v-if="canGoPrev" @click="handlePrev"> {{ $t('data-source.previousStep') }} </ElButton>
          <ElButton
            v-if="!isLastStep"
            type="primary"
            :disabled="!canGoNext"
            @click="handleNext"
          >
            {{ $t('data-source.nextStep') }}
          </ElButton>
          <ElButton
            v-if="isLastStep"
            type="primary"
            :loading="loading"
            @click="handleSave"
          >
            {{ $t('data-source.save') }}
          </ElButton>
          <ElButton @click="handleClose"> {{ $t('data-source.close') }} </ElButton>
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
        <div class="align-self-center w-[600px] translate-y-[-30%]">
          <div class="border-border bg-card rounded-lg border p-8 shadow-sm">
            <h3 class="mb-6 text-center text-lg font-medium">{{ $t('data-source.basicInfoConfig') }}</h3>
            <ElForm
              :model="formData"
              label-width="100px"
              label-position="right"
            >
              <ElFormItem :label="$t('data-source.dataSourceName')" required>
                <ElInput
                  v-model="formData.name"
                  :placeholder="$t('data-source.inputDataSourceName')"
                  clearable
                />
              </ElFormItem>
              <ElFormItem :label="$t('data-source.dataSourceType')" required>
                <ElInput
                  v-model="formData.code"
                  placeholder="请输入唯一编码，如 user_list"
                  :disabled="isEditMode"
                  clearable
                />
              </ElFormItem>
              <ElFormItem :label="$t('data-source.dataSourceType')" required>
                <ElRadioGroup v-model="formData.source_type" class="w-full">
                  <ElRadioButton
                    v-for="opt in sourceTypeOptions"
                    :key="opt.value"
                    :value="opt.value"
                  >
                    {{ opt.label }}
                  </ElRadioButton>
                </ElRadioGroup>
              </ElFormItem>
              <ElFormItem :label="$t('data-source.status')">
                <ElSwitch
                  v-model="formData.status"
                  :active-text="$t('data-source.enable')"
                  :inactive-text="$t('data-source.disable')"
                />
              </ElFormItem>
              <ElFormItem :label="$t('data-source.dataSourceDescription')">
                <ElInput
                  v-model="formData.description"
                  type="textarea"
                  :rows="3"
                  :placeholder="$t('data-source.inputDataSourceDescription')"
                />
              </ElFormItem>
            </ElForm>
          </div>
        </div>
      </div>

      <!-- 步骤2: 数据源配置 -->
      <div v-show="currentStep === 1" class="h-full overflow-hidden">
        <!-- SQL 类型：使用 Splitter 布局 -->
        <template v-if="formData.source_type === 'sql'">
          <ElSplitter class="h-full">
            <!-- 左侧面板：数据库结构 -->
            <ElSplitterPanel :size="20" class="border-border border-r">
              <DbSchemaPanel
                @insert-table="handleInsertTable"
                @insert-field="handleInsertField"
                @select-context="handleSelectContext"
              />
            </ElSplitterPanel>

            <!-- 右侧面板：SQL 编辑器 + 配置 -->
            <ElSplitterPanel :size="80">
              <ElSplitter layout="vertical" class="h-full">
                <!-- 右上：SQL 编辑器 -->
                <ElSplitterPanel :size="55" :min="30">
                  <div class="bg-card flex h-full flex-col">
                    <!-- 工具栏 -->
                    <div
                      class="border-border flex items-center justify-between border-b px-4 py-2"
                    >
                      <div class="flex items-center gap-4">
                        <span class="text-sm font-medium">{{ $t('data-source.dbSchema') }}:</span>
                        <div class="flex items-center gap-2">
                          <ElTag v-if="dbContext" type="primary" size="small">
                            {{ dbContextDisplay }}
                          </ElTag>
                          <span v-else class="text-muted-foreground text-sm">
                            {{ $t('data-source.selectDbSchema') }}
                          </span>
                        </div>
                      </div>
                      <ElButton
                        type="primary"
                        size="small"
                        :icon="Play"
                        :loading="testLoading"
                        @click="handleQuickTest"
                      >
                        {{ $t('data-source.testConnection') }}
                      </ElButton>
                    </div>
                    <!-- SQL 编辑器 -->
                    <div class="flex-1 overflow-hidden p-3">
                      <textarea
                        ref="sqlEditorRef"
                        v-model="formData.sql_content"
                        class="border-border bg-background focus:border-primary h-full w-full resize-none rounded border p-3 font-mono text-sm focus:outline-none"
                        placeholder="SELECT u.id, u.username, u.nickname
FROM core_user u
WHERE u.is_deleted = 0
  AND (:status IS NULL OR u.status = :status)
ORDER BY u.sys_create_datetime DESC"
                      ></textarea>
                    </div>
                    <!-- 提示 -->
                    <div class="border-border border-t px-4 py-1.5">
                      <span class="text-muted-foreground text-xs">
                        {{ $t('data-source.tip') }}: {{ $t('data-source.useParamPlaceholder') }}
                        <code class="bg-muted rounded px-1">:param</code>
                        {{ $t('data-source.onlySelectQuery') }}
                      </span>
                    </div>
                  </div>
                </ElSplitterPanel>

                <!-- 右下：配置 Tabs -->
                <ElSplitterPanel :size="45" :min="25">
                  <div class="bg-card h-full overflow-hidden">
                    <ElTabs
                      v-model="configActiveTab"
                      class="sql-config-tabs h-full"
                    >
                      <!-- 参数定义 -->
                      <ElTabPane name="params" class="h-full">
                        <template #label>
                          <div class="flex items-center gap-1">
                            <Settings class="h-4 w-4" />
                            <span>{{ $t('data-source.paramDefinition') }}</span>
                          </div>
                        </template>
                        <ElScrollbar class="h-full">
                          <div class="p-4">
                            <div class="mb-3 flex items-center justify-between">
                              <span class="text-muted-foreground text-sm"
                                >{{ $t('data-source.defineDataSourceParams') }}</span
                              >
                              <ElButton
                                type="primary"
                                :icon="CirclePlus"
                                size="small"
                                @click="addParam"
                              >
                                {{ $t('data-source.addParam') }}
                              </ElButton>
                            </div>
                            <ElTable
                              :data="formData.params || []"
                              border
                              stripe
                              max-height="180"
                            >
                              <ElTableColumn :label="$t('data-source.paramName')" width="140">
                                <template #default="{ row }">
                                  <ElInput
                                    v-model="row.name"
                                    placeholder="name"
                                    size="small"
                                  />
                                </template>
                              </ElTableColumn>
                              <ElTableColumn :label="$t('data-source.paramLabel')" width="140">
                                <template #default="{ row }">
                                  <ElInput
                                    v-model="row.label"
                                    placeholder="名称"
                                    size="small"
                                  />
                                </template>
                              </ElTableColumn>
                              <ElTableColumn :label="$t('data-source.paramType')" width="110">
                                <template #default="{ row }">
                                  <ElSelect
                                    v-model="row.type"
                                    size="small"
                                    class="w-full"
                                  >
                                    <ElOption
                                      v-for="opt in paramTypeOptions"
                                      :key="opt.value"
                                      :label="opt.label"
                                      :value="opt.value"
                                    />
                                  </ElSelect>
                                </template>
                              </ElTableColumn>
                              <ElTableColumn :label="$t('data-source.paramValue')" width="120">
                                <template #default="{ row }">
                                  <ElInput
                                    v-model="row.default"
                                    placeholder="默认值"
                                    size="small"
                                  />
                                </template>
                              </ElTableColumn>
                              <ElTableColumn
                                :label="$t('data-source.required')"
                                width="70"
                                align="center"
                              >
                                <template #default="{ row }">
                                  <ElSwitch
                                    v-model="row.required"
                                    size="small"
                                  />
                                </template>
                              </ElTableColumn>
                              <ElTableColumn
                                :label="$t('data-source.action')"
                                width="70"
                                align="center"
                              >
                                <template #default="{ $index }">
                                  <ElButton
                                    type="danger"
                                    :icon="Trash"
                                    size="small"
                                    circle
                                    @click="removeParam($index)"
                                  />
                                </template>
                              </ElTableColumn>
                            </ElTable>
                          </div>
                        </ElScrollbar>
                      </ElTabPane>

                      <!-- 结果处理 -->
                      <ElTabPane name="result">
                        <template #label>
                          <div class="flex items-center gap-1">
                            <Settings class="h-4 w-4" />
                            <span>{{ $t('data-source.resultProcessing') }}</span>
                          </div>
                        </template>
                        <ElScrollbar class="h-full">
                          <div class="p-4">
                            <ElForm :model="formData" label-width="100px">
                              <ElFormItem :label="$t('data-source.resultType')">
                                <ElRadioGroup v-model="formData.result_type">
                                  <ElRadioButton
                                    v-for="opt in resultTypeOptions"
                                    :key="opt.value"
                                    :value="opt.value"
                                  >
                                    {{ opt.label }}
                                  </ElRadioButton>
                                </ElRadioGroup>
                              </ElFormItem>
                              <!-- 结果类型提示 -->
                              <ElAlert
                                v-if="formData.result_type === 'list'"
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeListDesc')"
                              />
                              <ElAlert
                                v-else-if="formData.result_type === 'tree'"
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeTreeDesc')"
                              />
                              <ElAlert
                                v-else-if="formData.result_type === 'object'"
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeObjectDesc')"
                              />
                              <ElAlert
                                v-else-if="formData.result_type === 'value'"
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeValueDesc')"
                              />
                              <ElAlert
                                v-else-if="
                                  formData.result_type === 'chart-axis'
                                "
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartAxisDesc')"
                              />
                              <ElAlert
                                v-else-if="formData.result_type === 'chart-pie'"
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartPieDesc')"
                              />
                              <ElAlert
                                v-else-if="
                                  formData.result_type === 'chart-gauge'
                                "
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartGaugeDesc')"
                              />
                              <ElAlert
                                v-else-if="
                                  formData.result_type === 'chart-radar'
                                "
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartRadarDesc')"
                              />
                              <ElAlert
                                v-else-if="
                                  formData.result_type === 'chart-scatter'
                                "
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartScatterDesc')"
                              />
                              <ElAlert
                                v-else-if="
                                  formData.result_type === 'chart-heatmap'
                                "
                                type="primary"
                                show-icon
                                class="mb-4"
                                :title="$t('data-source.resultTypeChartHeatmapDesc')"
                              />
                              <!-- 树形配置 -->
                              <template v-if="formData.result_type === 'tree'">
                                <ElDivider content-position="left">
                                  {{ $t('data-source.treeConversionConfig') }}
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="8">
                                    <ElFormItem label="ID字段">
                                      <ElInput
                                        v-model="formData.tree_config!.id_field"
                                        placeholder="id"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem label="父级字段">
                                      <ElInput
                                        v-model="
                                          formData.tree_config!.parent_field
                                        "
                                        placeholder="parent_id"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem label="子节点字段">
                                      <ElInput
                                        v-model="
                                          formData.tree_config!.children_field
                                        "
                                        placeholder="children"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                              </template>
                              <!-- 轴向图表配置 -->
                              <template
                                v-if="formData.result_type === 'chart-axis'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.axisChartConfig') }}
                                  <ElTooltip
                                    content="适用于折线图、柱状图、面积图"
                                  >
                                    <span
                                      class="text-muted-foreground ml-1 cursor-help"
                                      >(?)</span>
                                  </ElTooltip>
                                </ElDivider>
                                <ElFormItem :label="$t('data-source.xAxisField')">
                                  <ElInput
                                    v-model="formData.chart_config!.x_field"
                                    placeholder="如：month"
                                  />
                                </ElFormItem>
                                <ElFormItem :label="$t('data-source.seriesField')">
                                  <ElInput
                                    v-model="chartSeriesFieldsStr"
                                    :placeholder="$t('data-source.multipleFieldsComma', { example: 'sales,profit' })"
                                  />
                                  <div
                                    class="text-muted-foreground mt-1 text-xs"
                                  >
                                    {{ $t('data-source.dataFieldsForChart') }}
                                  </div>
                                </ElFormItem>
                                <ElFormItem :label="$t('data-source.seriesName')">
                                  <ElInput
                                    v-model="chartSeriesNamesStr"
                                    :placeholder="$t('data-source.multipleNamesComma', { example: '销售额,利润' })"
                                  />
                                  <div
                                    class="text-muted-foreground mt-1 text-xs"
                                  >
                                    {{ $t('data-source.optionalLegendNames') }}
                                  </div>
                                </ElFormItem>
                              </template>
                              <!-- 饼图配置 -->
                              <template
                                v-if="formData.result_type === 'chart-pie'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.pieChartConfig') }}
                                  <ElTooltip content="适用于饼图、漏斗图">
                                    <span
                                      class="text-muted-foreground ml-1 cursor-help"
                                      >(?)</span>
                                  </ElTooltip>
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.nameField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.name_field
                                        "
                                        placeholder="如：category"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.valueField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.value_field
                                        "
                                        placeholder="如：amount"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                              </template>
                              <!-- 仪表盘配置 -->
                              <template
                                v-if="formData.result_type === 'chart-gauge'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.gaugeChartConfig') }}
                                  <ElTooltip content="适用于仪表盘、进度图">
                                    <span
                                      class="text-muted-foreground ml-1 cursor-help"
                                      >(?)</span>
                                  </ElTooltip>
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.valueField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.value_field
                                        "
                                        placeholder="如：value"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.nameField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.name_field
                                        "
                                        :placeholder="$t('data-source.optionalName')"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.maxField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.max_field
                                        "
                                        :placeholder="$t('data-source.optionalMax')"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                              </template>
                              <!-- 雷达图配置 -->
                              <template
                                v-if="formData.result_type === 'chart-radar'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.radarChartConfig') }}
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.indicatorNameField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.indicator_field
                                        "
                                        placeholder="如：name"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.maxField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.max_field
                                        "
                                        placeholder="如：max"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                                <ElFormItem :label="$t('data-source.valueField')">
                                  <ElInput
                                    v-model="chartValueFieldsStr"
                                    :placeholder="$t('data-source.multipleFieldsComma', { example: 'budget,actual' })"
                                  />
                                  <div
                                    class="text-muted-foreground mt-1 text-xs"
                                  >
                                    {{ $t('data-source.oneFieldPerSeries') }}
                                  </div>
                                </ElFormItem>
                                <ElFormItem :label="$t('data-source.seriesName')">
                                  <ElInput
                                    v-model="chartSeriesNamesStr"
                                    :placeholder="$t('data-source.multipleNamesComma', { example: '预算,实际' })"
                                  />
                                </ElFormItem>
                              </template>
                              <!-- 散点图配置 -->
                              <template
                                v-if="formData.result_type === 'chart-scatter'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.scatterChartConfig') }}
                                  <ElTooltip content="适用于散点图、气泡图">
                                    <span
                                      class="text-muted-foreground ml-1 cursor-help"
                                      >(?)</span>
                                  </ElTooltip>
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.xCoordinateField')">
                                      <ElInput
                                        v-model="formData.chart_config!.x_field"
                                        placeholder="如：x"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.yCoordinateField')">
                                      <ElInput
                                        v-model="formData.chart_config!.y_field"
                                        placeholder="如：y"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                                <ElRow :gutter="16">
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.sizeField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.size_field
                                        "
                                        :placeholder="$t('data-source.optionalBubbleChart')"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="12">
                                    <ElFormItem :label="$t('data-source.nameField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.name_field
                                        "
                                        :placeholder="$t('data-source.optionalName')"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                              </template>
                              <!-- 热力图配置 -->
                              <template
                                v-if="formData.result_type === 'chart-heatmap'"
                              >
                                <ElDivider content-position="left">
                                  {{ $t('data-source.heatmapChartConfig') }}
                                </ElDivider>
                                <ElRow :gutter="16">
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.xCoordinateField')">
                                      <ElInput
                                        v-model="formData.chart_config!.x_field"
                                        placeholder="如：x"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.yCoordinateField')">
                                      <ElInput
                                        v-model="formData.chart_config!.y_field"
                                        placeholder="如：y"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                  <ElCol :span="8">
                                    <ElFormItem :label="$t('data-source.valueField')">
                                      <ElInput
                                        v-model="
                                          formData.chart_config!.value_field
                                        "
                                        placeholder="如：value"
                                      />
                                    </ElFormItem>
                                  </ElCol>
                                </ElRow>
                              </template>
                              <!-- 字段映射 -->
                              <ElDivider content-position="left">
                                {{ $t('data-source.fieldMapping') }}
                                <ElTooltip
                                  :content="$t('data-source.fieldNameMapping')"
                                >
                                  <span
                                    class="text-muted-foreground ml-1 cursor-help"
                                    >(?)</span
                                  >
                                </ElTooltip>
                              </ElDivider>
                              <div class="mb-2">
                                <ElButton
                                  type="primary"
                                  :icon="CirclePlus"
                                  size="small"
                                  @click="addFieldMapping"
                                >
                                  {{ $t('data-source.addMapping') }}
                                </ElButton>
                              </div>
                              <div
                                v-for="(_, key) in formData.field_mapping"
                                :key="key"
                                class="mb-2 flex items-center gap-2"
                              >
                                <ElInput
                                  :model-value="key"
                                  :placeholder="$t('data-source.originalField')"
                                  class="w-40"
                                  @update:model-value="
                                    (v: string) =>
                                      updateFieldMappingKey(key as string, v)
                                  "
                                />
                                <span class="text-muted-foreground">-></span>
                                <ElInput
                                  v-model="
                                    formData.field_mapping![key as string]
                                  "
                                  :placeholder="$t('data-source.mappedField')"
                                  class="w-40"
                                />
                                <ElButton
                                  type="danger"
                                  :icon="Trash"
                                  size="small"
                                  circle
                                  @click="removeFieldMapping(key as string)"
                                />
                              </div>
                              <!-- 缓存配置 -->
                              <ElDivider content-position="left">
                                {{ $t('data-source.cacheConfig') }}
                              </ElDivider>
                              <ElRow :gutter="16">
                                <ElCol :span="8">
                                  <ElFormItem :label="$t('data-source.enableCache')">
                                    <ElSwitch
                                      v-model="formData.cache_enabled"
                                    />
                                  </ElFormItem>
                                </ElCol>
                                <ElCol :span="16">
                                  <ElFormItem
                                    v-if="formData.cache_enabled"
                                    :label="$t('data-source.cacheTime')"
                                  >
                                    <ElInputNumber
                                      v-model="formData.cache_ttl"
                                      :min="0"
                                      :max="86400"
                                    />
                                    <span
                                      class="text-muted-foreground ml-2 text-xs"
                                      >{{ $t('data-source.cacheTimeUnit') }}</span
                                    >
                                  </ElFormItem>
                                </ElCol>
                              </ElRow>
                            </ElForm>
                          </div>
                        </ElScrollbar>
                      </ElTabPane>

                      <!-- 测试 -->
                      <ElTabPane name="test">
                        <template #label>
                          <div class="flex items-center gap-1">
                            <Play class="h-4 w-4" />
                            <span>{{ $t('data-source.test') }}</span>
                          </div>
                        </template>
                        <ElScrollbar class="h-full">
                          <div class="space-y-4 p-4">
                            <!-- 测试参数 -->
                            <ElCard
                              v-if="
                                formData.params && formData.params.length > 0
                              "
                              shadow="never"
                            >
                              <template #header>
                                <span class="text-sm font-medium"
                                  >{{ $t('data-source.testParams') }}</span
                                >
                              </template>
                              <ElForm label-width="100px">
                                <ElRow :gutter="16">
                                  <ElCol
                                    v-for="param in formData.params"
                                    :key="param.name"
                                    :span="12"
                                  >
                                    <ElFormItem
                                      :label="param.label || param.name"
                                    >
                                      <ElInput
                                        v-model="testParams[param.name]"
                                        :placeholder="
                                          param.default !== null
                                            ? String(param.default)
                                            : ''
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
                                :loading="testLoading"
                                @click="handleTest"
                              >
                                {{ $t('data-source.executeTest') }}
                              </ElButton>
                            </div>
                            <!-- 测试结果 -->
                            <ElCard v-if="testResult" shadow="never">
                              <template #header>
                                <div class="flex items-center justify-between">
                                  <span class="text-sm font-medium"
                                    >{{ $t('data-source.testResult') }}</span
                                  >
                                  <ElTag
                                    :type="
                                      testResult.success ? 'success' : 'danger'
                                    "
                                    size="small"
                                  >
                                    {{ testResult.success ? $t('data-source.success') : $t('data-source.failed') }}
                                  </ElTag>
                                </div>
                              </template>
                              <div
                                class="text-muted-foreground flex items-center gap-2 text-sm"
                              >
                                <span>{{ $t('data-source.returnedData', { count: testResult.total }) }}</span>
                                <ElTag
                                  v-if="testResult.total >= testResult.limited"
                                  type="warning"
                                  size="small"
                                >
                                  {{ $t('data-source.reachedLimit', { limit: testResult.limited }) }}
                                </ElTag>
                              </div>
                              <ElScrollbar max-height="150px" class="mt-2">
                                <pre class="bg-muted rounded p-3 text-xs">{{
                                  JSON.stringify(testResult.data, null, 2)
                                }}</pre>
                              </ElScrollbar>
                            </ElCard>
                          </div>
                        </ElScrollbar>
                      </ElTabPane>
                    </ElTabs>
                  </div>
                </ElSplitterPanel>
              </ElSplitter>
            </ElSplitterPanel>
          </ElSplitter>
        </template>

        <!-- API/静态数据类型：保持原有布局 -->
        <div v-else class="flex h-full flex-col overflow-hidden p-4">
          <!-- 主配置区 -->
          <div
            class="border-border bg-card mb-4 flex-shrink-0 rounded-lg border p-4"
          >
            <!-- API 配置 -->
            <template v-if="formData.source_type === 'api'">
              <div class="mb-3 flex items-center justify-between">
                <span class="text-sm font-medium">API 配置</span>
                <ElButton
                  type="primary"
                  size="small"
                  :icon="Play"
                  :loading="testLoading"
                  @click="handleQuickTest"
                >
                  测试
                </ElButton>
              </div>
              <ElForm :model="formData" label-width="100px">
                <ElFormItem label="请求地址" required>
                  <ElInput
                    v-model="formData.api_url"
                    placeholder="https://api.example.com/data"
                  >
                    <template #prepend>
                      <ElSelect
                        v-model="formData.api_method"
                        style="width: 90px"
                      >
                        <ElOption
                          v-for="opt in httpMethodOptions"
                          :key="opt.value"
                          :label="opt.label"
                          :value="opt.value"
                        />
                      </ElSelect>
                    </template>
                  </ElInput>
                </ElFormItem>
                <ElRow :gutter="16">
                  <ElCol :span="12">
                    <ElFormItem label="超时时间">
                      <ElInputNumber
                        v-model="formData.api_timeout"
                        :min="1"
                        :max="300"
                        class="w-full"
                      />
                      <span class="text-muted-foreground ml-2 text-xs">秒</span>
                    </ElFormItem>
                  </ElCol>
                  <ElCol :span="12">
                    <ElFormItem label="数据路径">
                      <ElInput
                        v-model="formData.api_data_path"
                        placeholder="如 data.list"
                      />
                    </ElFormItem>
                  </ElCol>
                </ElRow>
                <ElFormItem label="请求头">
                  <ElInput
                    v-model="apiHeadersStr"
                    type="textarea"
                    :rows="3"
                    placeholder='{"Authorization": "Bearer {token}"}'
                    class="font-mono"
                  />
                </ElFormItem>
                <ElFormItem
                  v-if="formData.api_method === 'POST'"
                  label="请求体"
                >
                  <ElInput
                    v-model="apiBodyStr"
                    type="textarea"
                    :rows="3"
                    placeholder='{"page": 1, "pageSize": 10}'
                    class="font-mono"
                  />
                </ElFormItem>
              </ElForm>
            </template>

            <!-- 静态数据配置 -->
            <template v-else-if="formData.source_type === 'static'">
              <div class="mb-3 flex items-center justify-between">
                <span class="text-sm font-medium">静态数据 (JSON 数组)</span>
                <ElButton
                  type="primary"
                  size="small"
                  :icon="Play"
                  :loading="testLoading"
                  @click="handleQuickTest"
                >
                  测试
                </ElButton>
              </div>
              <ElInput
                v-model="staticDataStr"
                type="textarea"
                :rows="12"
                placeholder='[
  {"id": 1, "name": "选项1", "value": "1"},
  {"id": 2, "name": "选项2", "value": "2"}
]'
                class="font-mono"
              />
            </template>
          </div>

          <!-- 底部 Tabs: 参数定义 / 结果处理 / 测试 -->
          <div
            class="border-border bg-card flex-1 overflow-hidden rounded-lg border"
          >
            <ElTabs v-model="configActiveTab" class="h-full">
              <!-- 参数定义 -->
              <ElTabPane name="params" class="h-full">
                <template #label>
                  <div class="flex items-center gap-1">
                    <Settings class="h-4 w-4" />
                    <span>参数定义</span>
                  </div>
                </template>
                <div class="p-4">
                  <div class="mb-3 flex items-center justify-between">
                    <span class="text-muted-foreground text-sm"
                      >定义数据源可接收的参数</span
                    >
                    <ElButton
                      type="primary"
                      :icon="CirclePlus"
                      size="small"
                      @click="addParam"
                    >
                      添加参数
                    </ElButton>
                  </div>
                  <ElTable
                    :data="formData.params || []"
                    border
                    stripe
                    max-height="200"
                  >
                    <ElTableColumn label="参数名" width="140">
                      <template #default="{ row }">
                        <ElInput
                          v-model="row.name"
                          placeholder="name"
                          size="small"
                        />
                      </template>
                    </ElTableColumn>
                    <ElTableColumn label="显示名" width="140">
                      <template #default="{ row }">
                        <ElInput
                          v-model="row.label"
                          placeholder="名称"
                          size="small"
                        />
                      </template>
                    </ElTableColumn>
                    <ElTableColumn label="类型" width="110">
                      <template #default="{ row }">
                        <ElSelect
                          v-model="row.type"
                          size="small"
                          class="w-full"
                        >
                          <ElOption
                            v-for="opt in paramTypeOptions"
                            :key="opt.value"
                            :label="opt.label"
                            :value="opt.value"
                          />
                        </ElSelect>
                      </template>
                    </ElTableColumn>
                    <ElTableColumn label="默认值" width="120">
                      <template #default="{ row }">
                        <ElInput
                          v-model="row.default"
                          placeholder="默认值"
                          size="small"
                        />
                      </template>
                    </ElTableColumn>
                    <ElTableColumn label="必填" width="70" align="center">
                      <template #default="{ row }">
                        <ElSwitch v-model="row.required" size="small" />
                      </template>
                    </ElTableColumn>
                    <ElTableColumn label="操作" width="70" align="center">
                      <template #default="{ $index }">
                        <ElButton
                          type="danger"
                          :icon="Trash"
                          size="small"
                          circle
                          @click="removeParam($index)"
                        />
                      </template>
                    </ElTableColumn>
                  </ElTable>
                </div>
              </ElTabPane>

              <!-- 结果处理 -->
              <ElTabPane name="result">
                <template #label>
                  <div class="flex items-center gap-1">
                    <Settings class="h-4 w-4" />
                    <span>结果处理</span>
                  </div>
                </template>
                <ElScrollbar class="h-full">
                  <div class="p-4">
                    <ElForm :model="formData" label-width="100px">
                      <ElFormItem label="结果类型">
                        <ElRadioGroup v-model="formData.result_type">
                          <ElRadioButton
                            v-for="opt in resultTypeOptions"
                            :key="opt.value"
                            :value="opt.value"
                          >
                            {{ opt.label }}
                          </ElRadioButton>
                        </ElRadioGroup>
                      </ElFormItem>

                      <!-- 树形配置 -->
                      <template v-if="formData.result_type === 'tree'">
                        <ElDivider content-position="left">
                          树形转换配置
                        </ElDivider>
                        <ElRow :gutter="16">
                          <ElCol :span="8">
                            <ElFormItem label="ID字段">
                              <ElInput
                                v-model="formData.tree_config!.id_field"
                                placeholder="id"
                              />
                            </ElFormItem>
                          </ElCol>
                          <ElCol :span="8">
                            <ElFormItem label="父级字段">
                              <ElInput
                                v-model="formData.tree_config!.parent_field"
                                placeholder="parent_id"
                              />
                            </ElFormItem>
                          </ElCol>
                          <ElCol :span="8">
                            <ElFormItem label="子节点字段">
                              <ElInput
                                v-model="formData.tree_config!.children_field"
                                placeholder="children"
                              />
                            </ElFormItem>
                          </ElCol>
                        </ElRow>
                      </template>

                      <!-- 字段映射 -->
                      <ElDivider content-position="left">
                        字段映射
                        <ElTooltip
                          content="将原字段名映射为新字段名，如 id -> value"
                        >
                          <span class="text-muted-foreground ml-1 cursor-help"
                            >(?)</span
                          >
                        </ElTooltip>
                      </ElDivider>
                      <div class="mb-2">
                        <ElButton
                          type="primary"
                          :icon="CirclePlus"
                          size="small"
                          @click="addFieldMapping"
                        >
                          添加映射
                        </ElButton>
                      </div>
                      <div
                        v-for="(_, key) in formData.field_mapping"
                        :key="key"
                        class="mb-2 flex items-center gap-2"
                      >
                        <ElInput
                          :model-value="key"
                          placeholder="原字段"
                          class="w-40"
                          @change="
                            (v: string) =>
                              updateFieldMappingKey(key as string, v)
                          "
                        />
                        <span class="text-muted-foreground">-></span>
                        <ElInput
                          v-model="formData.field_mapping![key as string]"
                          placeholder="新字段"
                          class="w-40"
                        />
                        <ElButton
                          type="danger"
                          :icon="Trash"
                          size="small"
                          circle
                          @click="removeFieldMapping(key as string)"
                        />
                      </div>

                      <!-- 缓存配置 -->
                      <ElDivider content-position="left">缓存配置</ElDivider>
                      <ElRow :gutter="16">
                        <ElCol :span="8">
                          <ElFormItem label="启用缓存">
                            <ElSwitch v-model="formData.cache_enabled" />
                          </ElFormItem>
                        </ElCol>
                        <ElCol :span="16">
                          <ElFormItem
                            v-if="formData.cache_enabled"
                            label="缓存时间"
                          >
                            <ElInputNumber
                              v-model="formData.cache_ttl"
                              :min="0"
                              :max="86400"
                            />
                            <span class="text-muted-foreground ml-2 text-xs"
                              >秒（0表示不缓存）</span
                            >
                          </ElFormItem>
                        </ElCol>
                      </ElRow>
                    </ElForm>
                  </div>
                </ElScrollbar>
              </ElTabPane>

              <!-- 测试 -->
              <ElTabPane name="test">
                <template #label>
                  <div class="flex items-center gap-1">
                    <Play class="h-4 w-4" />
                    <span>测试</span>
                  </div>
                </template>
                <ElScrollbar class="h-full">
                  <div class="space-y-4 p-4">
                    <!-- 测试参数 -->
                    <ElCard
                      v-if="formData.params && formData.params.length > 0"
                      shadow="never"
                    >
                      <template #header>
                        <span class="text-sm font-medium">测试参数</span>
                      </template>
                      <ElForm label-width="100px">
                        <ElRow :gutter="16">
                          <ElCol
                            v-for="param in formData.params"
                            :key="param.name"
                            :span="12"
                          >
                            <ElFormItem :label="param.label || param.name">
                              <ElInput
                                v-model="testParams[param.name]"
                                :placeholder="
                                  param.default !== null
                                    ? String(param.default)
                                    : ''
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
                        :loading="testLoading"
                        @click="handleTest"
                      >
                        执行测试
                      </ElButton>
                    </div>

                    <!-- 测试结果 -->
                    <ElCard v-if="testResult" shadow="never">
                      <template #header>
                        <div class="flex items-center justify-between">
                          <span class="text-sm font-medium">测试结果</span>
                          <ElTag
                            :type="testResult.success ? 'success' : 'danger'"
                            size="small"
                          >
                            {{ testResult.success ? '成功' : '失败' }}
                          </ElTag>
                        </div>
                      </template>
                      <div
                        class="text-muted-foreground flex items-center gap-2 text-sm"
                      >
                        <span>返回 {{ testResult.total }} 条数据</span>
                        <ElTag
                          v-if="testResult.total >= testResult.limited"
                          type="warning"
                          size="small"
                        >
                          已达上限 {{ testResult.limited }} 条
                        </ElTag>
                      </div>
                      <ElScrollbar max-height="200px" class="mt-2">
                        <pre class="bg-muted rounded p-3 text-xs">{{
                          JSON.stringify(testResult.data, null, 2)
                        }}</pre>
                      </ElScrollbar>
                    </ElCard>
                  </div>
                </ElScrollbar>
              </ElTabPane>
            </ElTabs>
          </div>
        </div>
      </div>
    </div>
  </ElDialog>
</template>

<style scoped>
:deep(.el-tabs__header) {
  padding: 0 16px;
  margin-bottom: 0;
  border-bottom: 1px solid var(--el-border-color);
}

:deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow: hidden;
}

:deep(.el-tab-pane) {
  height: 100%;
  overflow: hidden;
}

:deep(.el-textarea__inner) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}

/* SQL 配置区域的 Tabs 样式 */
:deep(.sql-config-tabs .el-tabs__header) {
  padding: 0 12px;
  background-color: var(--el-fill-color-lighter);
}

:deep(.sql-config-tabs .el-tabs__content) {
  height: calc(100% - 40px);
}

/* 隐藏分隔线 - 将分隔线设置为透明 */
:deep(.el-splitter-bar__dragger)::before,
:deep(.el-splitter-bar__dragger)::after {
  background-color: transparent !important;
}

/* 隐藏折叠图标 */
:deep(.el-splitter-bar__collapse-icon) {
  background: transparent !important;
  opacity: 0 !important;
}
</style>
