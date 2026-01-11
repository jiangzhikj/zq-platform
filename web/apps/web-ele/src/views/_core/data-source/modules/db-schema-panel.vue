<script lang="ts" setup>
import type { ColumnInfo } from '#/api/core/database-manager';

/**
 * 数据库结构面板 - 用于数据源编辑器
 * 复用 data-source-config 的数据库树逻辑，简化为只显示树形结构
 * 点击表名或字段名可插入到 SQL 编辑器
 */
import { onMounted, ref } from 'vue';

import { $t } from '@vben/locales';
import { Database, RefreshCw } from '@vben/icons';

import {
  ElButton,
  ElIcon,
  ElScrollbar,
  ElSplitter,
  ElSplitterPanel,
  ElTag,
  ElTooltip,
  ElTree,
} from 'element-plus';

import {
  getDatabaseConfigsApi,
  getDatabasesApi,
  getSchemasApi,
  getTableColumnsApi,
  getTablesApi,
} from '#/api/core/database-manager';
import { getNodeIcon, getNodeIconClass } from '#/utils/database-tree';

// 树节点类型
interface TreeNode {
  id: string;
  label: string;
  type: 'connection' | 'database' | 'field' | 'schema' | 'table';
  isLeaf: boolean;
  meta?: {
    database?: string;
    dbName?: string;
    dbType?: string;
    fieldType?: string;
    schema?: string;
    table?: string;
  };
  children?: TreeNode[];
}

// 字段信息
interface FieldInfo {
  name: string;
  type: string;
  comment: string;
  isPrimaryKey: boolean;
}

const emit = defineEmits<{
  'insert-field': [tableName: string, fieldName: string];
  'insert-table': [tableName: string];
  'select-context': [
    context: { database?: string; dbName: string; schema?: string },
  ];
}>();

// 树相关
const treeRef = ref();
const treeData = ref<TreeNode[]>([]);
const loading = ref(false);

// 树配置
const treeProps = {
  label: 'label',
  children: 'children',
  isLeaf: 'isLeaf',
};

// 当前选中的表节点（用于显示字段预览）
const selectedTableNode = ref<null | TreeNode>(null);
const previewFields = ref<FieldInfo[]>([]);
const previewLoading = ref(false);

// 当前选中的数据库上下文
const currentContext = ref<null | {
  database?: string;
  dbName: string;
  schema?: string;
}>(null);

// 加载数据库配置（根节点）
async function loadDatabaseConfigs() {
  loading.value = true;
  try {
    const configs = await getDatabaseConfigsApi();
    treeData.value = configs.map((config) => ({
      id: `conn-${config.db_name}`,
      label: config.name,
      type: 'connection' as const,
      isLeaf: false,
      meta: {
        dbName: config.db_name,
        dbType: config.db_type,
      },
    }));
  } catch (error) {
    console.error('Failed to load database configs:', error);
  } finally {
    loading.value = false;
  }
}

// 加载数据库列表
async function loadDatabases(dbName: string, dbType?: string) {
  try {
    const databases = await getDatabasesApi(dbName);
    return databases.map((db) => ({
      id: `db-${dbName}-${db.name}`,
      label: db.name,
      type: 'database' as const,
      isLeaf: false,
      meta: {
        dbName,
        dbType,
        database: db.name,
      },
    }));
  } catch (error) {
    console.error('Failed to load databases:', error);
    return [];
  }
}

// 加载Schema列表
async function loadSchemas(dbName: string, database: string, dbType?: string) {
  try {
    const schemas = await getSchemasApi(dbName, database);
    return schemas.map((schema) => ({
      id: `schema-${dbName}-${database}-${schema.name}`,
      label: schema.name,
      type: 'schema' as const,
      isLeaf: false,
      meta: {
        dbName,
        dbType,
        database,
        schema: schema.name,
      },
    }));
  } catch (error) {
    console.error('Failed to load schemas:', error);
    return [];
  }
}

// 加载表列表
async function loadTables(
  dbName: string,
  database: string,
  schema?: string,
  dbType?: string,
) {
  try {
    const tableList = await getTablesApi(dbName, database, schema);
    return tableList.map((table) => ({
      id: `table-${dbName}-${database}-${schema || ''}-${table.table_name}`,
      label: table.table_name,
      type: 'table' as const,
      isLeaf: false, // 表节点可以展开显示字段
      meta: {
        dbName,
        dbType,
        database,
        schema: schema || table.schema_name,
        table: table.table_name,
      },
    }));
  } catch (error) {
    console.error('Failed to load tables:', error);
    return [];
  }
}

// 加载表字段
async function loadTableFields(
  dbName: string,
  tableName: string,
  database?: string,
  schema?: string,
) {
  try {
    const columns = await getTableColumnsApi(
      dbName,
      tableName,
      database,
      schema,
    );
    return columns.map((col: ColumnInfo) => ({
      id: `field-${dbName}-${database}-${schema}-${tableName}-${col.column_name}`,
      label: col.column_name,
      type: 'field' as const,
      isLeaf: true,
      meta: {
        dbName,
        database,
        schema,
        table: tableName,
        fieldType: col.data_type,
      },
    }));
  } catch (error) {
    console.error('Failed to load table fields:', error);
    return [];
  }
}

// 懒加载子节点
async function loadNode(node: any, resolve: any) {
  if (node.level === 0) {
    resolve(treeData.value);
    return;
  }

  const nodeData = node.data as TreeNode;
  const { type, meta } = nodeData;

  if (!meta) {
    resolve([]);
    return;
  }

  try {
    if (type === 'connection' && meta.dbName) {
      const nodes = await loadDatabases(meta.dbName, meta.dbType);
      resolve(nodes);
      return;
    }

    if (type === 'database' && meta.dbName && meta.database) {
      const dbType = meta.dbType?.toLowerCase();
      if (dbType === 'postgresql' || dbType === 'sqlserver') {
        const nodes = await loadSchemas(
          meta.dbName,
          meta.database,
          meta.dbType,
        );
        resolve(nodes);
      } else {
        const nodes = await loadTables(
          meta.dbName,
          meta.database,
          undefined,
          meta.dbType,
        );
        resolve(nodes);
      }
      return;
    }

    if (type === 'schema' && meta.dbName && meta.database) {
      const nodes = await loadTables(
        meta.dbName,
        meta.database,
        meta.schema,
        meta.dbType,
      );
      resolve(nodes);
      return;
    }

    if (type === 'table' && meta.dbName && meta.table) {
      const nodes = await loadTableFields(
        meta.dbName,
        meta.table,
        meta.database,
        meta.schema,
      );
      resolve(nodes);
      return;
    }

    resolve([]);
  } catch (error) {
    console.error('Failed to load node:', error);
    resolve([]);
  }
}

// 更新数据库上下文
function updateContext(meta: TreeNode['meta']) {
  if (meta?.dbName) {
    currentContext.value = {
      dbName: meta.dbName,
      database: meta.database,
      schema: meta.schema,
    };
    emit('select-context', currentContext.value);
  }
}

// 节点点击 - 预览表字段或插入
async function handleNodeClick(data: TreeNode) {
  // 更新上下文（数据库/schema/表）
  if (data.meta && ['database', 'schema', 'table'].includes(data.type)) {
    updateContext(data.meta);
  }

  if (data.type === 'table' && data.meta) {
    // 点击表名 - 插入表名
    emit('insert-table', data.meta.table!);

    // 同时更新预览
    selectedTableNode.value = data;
    previewLoading.value = true;

    try {
      const columns = await getTableColumnsApi(
        data.meta.dbName!,
        data.meta.table!,
        data.meta.database,
        data.meta.schema,
      );
      previewFields.value = columns.map((col: ColumnInfo) => ({
        name: col.column_name,
        type: col.data_type,
        comment: col.description || '',
        isPrimaryKey: col.is_primary_key,
      }));
    } catch (error) {
      console.error('Failed to load columns:', error);
      previewFields.value = [];
    } finally {
      previewLoading.value = false;
    }
  } else if (data.type === 'field' && data.meta) {
    // 点击字段名 - 插入字段名
    emit('insert-field', data.meta.table!, data.label);
  }
}

// 刷新树
async function refreshTree() {
  await loadDatabaseConfigs();
}

// 初始化
onMounted(() => {
  loadDatabaseConfigs();
});

defineExpose({
  refresh: refreshTree,
});
</script>

<template>
  <ElSplitter layout="vertical" class="bg-card h-full">
    <!-- 上部：数据库结构树 -->
    <ElSplitterPanel :size="65" :min="40">
      <div class="flex h-full flex-col">
        <!-- 标题 -->
        <div
          class="border-border flex items-center justify-between border-b px-3 py-2"
        >
          <div class="flex items-center gap-2">
            <ElIcon><Database /></ElIcon>
            <span class="text-sm font-medium">{{ $t('data-source.dbSchema') }}</span>
          </div>
          <ElTooltip :content="$t('data-source.refresh')">
            <ElButton
              :icon="RefreshCw"
              link
              size="small"
              @click="refreshTree"
            />
          </ElTooltip>
        </div>

        <!-- 树形结构 -->
        <ElScrollbar class="flex-1">
          <div v-if="loading" class="flex h-32 items-center justify-center">
            <span class="text-muted-foreground text-sm">{{ $t('data-source.loading') }}</span>
          </div>
          <ElTree
            v-else
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            :load="loadNode"
            node-key="id"
            lazy
            highlight-current
            class="p-2"
            @node-click="handleNodeClick"
          >
            <template #default="{ data }">
              <div class="flex w-full items-center justify-between pr-2">
                <div class="flex items-center gap-2">
                  <component
                    :is="getNodeIcon(data.type)"
                    class="h-4 w-4"
                    :class="getNodeIconClass(data.type)"
                  />
                  <span class="text-sm">{{ data.label }}</span>
                  <!-- 字段类型提示 -->
                  <span
                    v-if="data.type === 'field' && data.meta?.fieldType"
                    class="text-muted-foreground text-[10px]"
                  >
                    {{ data.meta.fieldType }}
                  </span>
                </div>
              </div>
            </template>
          </ElTree>
        </ElScrollbar>
      </div>
    </ElSplitterPanel>

    <!-- 下部：字段预览 -->
    <ElSplitterPanel :size="35" :min="20">
      <div class="flex h-full flex-col">
        <!-- 标题 -->
        <div
          class="border-border bg-muted/30 flex items-center justify-between border-b px-3 py-2"
        >
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium">
              {{
                selectedTableNode
                  ? `${selectedTableNode.label} ${$t('data-source.columns')}`
                  : $t('data-source.fieldPreview')
              }}
            </span>
          </div>
          <span
            v-if="!selectedTableNode"
            class="text-muted-foreground text-[10px]"
          >
            {{ $t('data-source.clickTableToView') }}
          </span>
        </div>

        <!-- 字段列表 -->
        <ElScrollbar class="flex-1">
          <div
            v-if="!selectedTableNode"
            class="flex h-full items-center justify-center"
          >
            <span class="text-muted-foreground text-xs">{{ $t('data-source.selectTable') }}</span>
          </div>
          <div
            v-else-if="previewLoading"
            class="flex h-20 items-center justify-center"
          >
            <span class="text-muted-foreground text-xs">{{ $t('data-source.loading') }}</span>
          </div>
          <div v-else class="p-2">
            <div
              v-for="field in previewFields"
              :key="field.name"
              class="hover:bg-muted/50 flex cursor-pointer items-center justify-between rounded px-2 py-1.5 text-xs"
              @click="
                emit(
                  'insert-field',
                  selectedTableNode.meta?.table || '',
                  field.name,
                )
              "
            >
              <div class="flex items-center gap-2">
                <span
                  class="font-mono font-medium"
                  :class="{ 'text-primary': field.isPrimaryKey }"
                >
                  {{ field.name }}
                </span>
                <ElTag v-if="field.isPrimaryKey" size="small" type="warning">
                  PK
                </ElTag>
              </div>
              <span class="text-muted-foreground">{{ field.type }}</span>
            </div>
            <div
              v-if="previewFields.length === 0"
              class="text-muted-foreground py-4 text-center text-xs"
            >
              {{ $t('data-source.noFieldInfo') }}
            </div>
          </div>
        </ElScrollbar>

        <!-- 提示 -->
        <div class="border-border border-t px-3 py-1.5">
          <p class="text-muted-foreground text-[10px]">
            {{ $t('data-source.clickFieldToInsert') }}
          </p>
        </div>
      </div>
    </ElSplitterPanel>
  </ElSplitter>
</template>

<style scoped>
/* 调整树节点高度 */
:deep(.el-tree-node__content) {
  height: 28px;
  line-height: 28px;
  border-radius: 4px;
}

/* 选中节点的背景色 */
:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: var(--el-color-primary-light-9);
}

/* 悬停效果 */
:deep(.el-tree-node__content:hover) {
  background-color: var(--el-fill-color-light);
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
