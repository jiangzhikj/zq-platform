import { computed, nextTick, ref } from 'vue';

import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';

import { $t } from '@vben/locales';

// 数据源类型
export type DataSourceType = 'api' | 'dataSource' | 'static' | 'upload';

// 字段映射配置
export interface FieldMapping {
  source: string; // API 返回的字段路径，支持 a.b.c 格式
  target: string; // 组件 props 中的字段名
}

// 数据源配置
export interface DataSourceConfig {
  type: DataSourceType;
  // 通用数据源配置
  dataSourceCode?: string; // 数据源编码
  // API 配置
  apiUrl?: string;
  apiMethod?: 'GET' | 'POST';
  apiHeaders?: Record<string, string>;
  apiParams?: Record<string, any>;
  apiBody?: Record<string, any>;
  // 数据处理
  dataPath?: string; // 响应数据路径，如 data.list
  fieldMappings?: FieldMapping[]; // 字段映射
  // 刷新配置
  refreshInterval?: number; // 刷新间隔（秒），0 表示不刷新
  refreshEnabled?: boolean; // 是否启用自动刷新
}

// Widget 类型
export type WidgetType =
  | 'announcement-list' // 公告列表
  | 'calendar' // 日历
  | 'chart-area' // 面积图
  | 'chart-bar' // 柱状图
  | 'chart-funnel' // 漏斗图
  | 'chart-gauge' // 仪表盘
  | 'chart-heatmap' // 热力图
  | 'chart-kline' // K线图
  | 'chart-line' // 折线图
  | 'chart-pie' // 饼图
  | 'chart-radar' // 雷达图
  | 'chart-ring' // 环形进度图
  | 'chart-sankey' // 桑基图
  | 'chart-scatter' // 散点图
  | 'clock' // 时钟
  | 'countdown' // 倒计时
  | 'data-table' // 数据表格
  | 'iframe' // iframe 嵌入
  | 'image' // 图片
  | 'image-carousel' // 图片轮播
  | 'notice-list' // 通知列表
  | 'progress-card' // 进度卡片
  | 'quick-links' // 快捷入口
  | 'ranking-list' // 排行榜
  | 'stat-card' // 统计卡片
  | 'todo-list' // 待办列表
  | 'video-player' // 视频播放器
  | 'weather' // 天气
  | 'welcome-card'; // 欢迎卡片

// 组件样式配置
export interface WidgetStyle {
  // 背景
  backgroundColor?: string;
  backgroundImage?: string;
  backgroundSize?: 'auto' | 'contain' | 'cover';
  // 边框
  borderWidth?: number;
  borderColor?: string;
  borderStyle?: 'dashed' | 'dotted' | 'none' | 'solid';
  borderRadius?: number;
  // 阴影
  shadowEnabled?: boolean;
  shadowColor?: string;
  shadowBlur?: number;
  shadowOffsetX?: number;
  shadowOffsetY?: number;
  // 内边距
  padding?: number;
  // 标题样式
  titleShow?: boolean;
  titleFontSize?: number;
  titleColor?: string;
  titleAlign?: 'center' | 'left' | 'right';
  titleFontWeight?: 'bold' | 'normal';
}

// 默认样式
export const defaultWidgetStyle: WidgetStyle = {
  backgroundColor: '',
  borderWidth: 0,
  borderColor: '',
  borderStyle: 'solid',
  borderRadius: 8,
  shadowEnabled: true,
  shadowColor: 'rgba(0, 0, 0, 0.1)',
  shadowBlur: 4,
  shadowOffsetX: 0,
  shadowOffsetY: 1,
  padding: 16,
  titleShow: true,
  titleFontSize: 14,
  titleColor: '',
  titleAlign: 'left',
  titleFontWeight: 'normal',
};

// Widget 配置
export interface DashboardWidget {
  id: string;
  type: WidgetType;
  i: string; // grid-layout 需要的唯一标识
  x: number; // 网格 x 坐标
  y: number; // 网格 y 坐标
  w: number; // 宽度（网格单位）
  h: number; // 高度（网格单位）
  minW?: number; // 最小宽度
  minH?: number; // 最小高度
  maxW?: number; // 最大宽度
  maxH?: number; // 最大高度
  title?: string; // 标题
  props: Record<string, any>; // 组件属性
  style?: WidgetStyle; // 样式配置
  dataSource?: DataSourceConfig;
}

// 仪表盘配置
export interface DashboardConfig {
  id: string;
  name: string;
  columns: number; // 网格列数
  rowHeight: number; // 行高
  margin: [number, number]; // 间距
  backgroundColor?: string; // 背景颜色
  showOuterMargin?: boolean; // 显示四周边距
  widgets: DashboardWidget[];
}

// 组件材料定义
export interface WidgetMaterial {
  type: WidgetType;
  title: string;
  icon: string;
  category: 'chart' | 'list' | 'widget';
  defaultW: number;
  defaultH: number;
  minW?: number;
  minH?: number;
  defaultProps: Record<string, any>;
}

// 预定义组件材料
export const widgetMaterials: WidgetMaterial[] = [
  // 数据展示
  {
    type: 'stat-card',
    title: $t('dashboard-design.material.widgets.statCard'),
    icon: 'CreditCard',
    category: 'widget',
    defaultW: 3,
    defaultH: 2,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.statTitle'),
      value: 0,
      prefix: '',
      suffix: '',
      trend: 0,
      trendLabel: $t('dashboard-design.material.defaultProps.trendLabel'),
      iconName: 'TrendingUp',
      iconColor: 'var(--el-color-primary)',
      bgColor: 'var(--el-bg-color)',
    },
  },
  {
    type: 'progress-card',
    title: $t('dashboard-design.material.widgets.progressCard'),
    icon: 'Activity',
    category: 'widget',
    defaultW: 3,
    defaultH: 2,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.progressTitle'),
      percentage: 75,
      status: '',
      strokeWidth: 12,
      showText: true,
    },
  },
  // 图表
  {
    type: 'chart-line',
    title: $t('dashboard-design.material.widgets.chartLine'),
    icon: 'TrendingUp',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.visitTrend'),
      // 图表配置
      smooth: true,
      showArea: false,
      showSymbol: true,
      symbolSize: 6,
      lineWidth: 2,
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      xAxisData: [
        $t('dashboard-design.months.jan'),
        $t('dashboard-design.months.feb'),
        $t('dashboard-design.months.mar'),
        $t('dashboard-design.months.apr'),
        $t('dashboard-design.months.may'),
        $t('dashboard-design.months.jun'),
        $t('dashboard-design.months.jul'),
        $t('dashboard-design.months.aug'),
        $t('dashboard-design.months.sep'),
        $t('dashboard-design.months.oct'),
        $t('dashboard-design.months.nov'),
        $t('dashboard-design.months.dec'),
      ],
      seriesData: [
        {
          name: $t('dashboard-design.widgets.chart.visits'),
          data: [
            820, 932, 901, 934, 1290, 1330, 1320, 1450, 1200, 1100, 1350, 1500,
          ],
        },
        {
          name: $t('dashboard-design.material.defaultProps.downloads'),
          data: [
            620, 732, 701, 734, 1090, 1130, 1120, 1250, 1000, 900, 1150, 1300,
          ],
        },
      ],
    },
  },
  {
    type: 'chart-bar',
    title: $t('dashboard-design.material.widgets.chartBar'),
    icon: 'BarChart2',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.salesStat'),
      // 图表配置
      horizontal: false,
      stack: false,
      barWidth: 'auto',
      barRadius: 4,
      showBackground: false,
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      xAxisData: [
        $t('dashboard-design.location.east'),
        $t('dashboard-design.location.south'),
        $t('dashboard-design.location.north'),
        $t('dashboard-design.location.central'),
        $t('dashboard-design.location.southwest'),
        $t('dashboard-design.location.northwest'),
        $t('dashboard-design.location.northeast'),
      ],
      seriesData: [
        { name: '2023', data: [320, 302, 301, 334, 390, 330, 320] },
        { name: '2024', data: [420, 382, 391, 434, 490, 430, 420] },
      ],
    },
  },
  {
    type: 'chart-pie',
    title: $t('dashboard-design.material.widgets.chartPie'),
    icon: 'PieChart',
    category: 'chart',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.trafficSource'),
      // 图表配置
      pieType: 'pie', // pie | ring | rose
      radius: ['0%', '70%'],
      showLabel: true,
      labelPosition: 'outside', // outside | inside
      // 图例
      showLegend: true,
      legendPosition: 'bottom',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      seriesData: [
        { name: $t('dashboard-design.material.defaultProps.searchEngine'), value: 1048 },
        { name: $t('dashboard-design.material.defaultProps.directAccess'), value: 735 },
        { name: $t('dashboard-design.material.defaultProps.emailMarketing'), value: 580 },
        { name: $t('dashboard-design.material.defaultProps.unionAds'), value: 484 },
        { name: $t('dashboard-design.material.defaultProps.videoAds'), value: 300 },
      ],
    },
  },
  {
    type: 'chart-gauge',
    title: $t('dashboard-design.material.widgets.chartGauge'),
    icon: 'Gauge',
    category: 'chart',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.sysLoad'),
      // 图表配置
      value: 72.5,
      min: 0,
      max: 100,
      unit: '%',
      splitNumber: 10,
      showProgress: true,
      // 颜色区间
      colorStops: [
        { offset: 0.3, color: '#67e0e3' },
        { offset: 0.7, color: '#37a2da' },
        { offset: 1, color: '#fd666d' },
      ],
      // 指针
      pointerWidth: 6,
      pointerLength: '60%',
    },
  },
  {
    type: 'chart-area',
    title: $t('dashboard-design.material.widgets.chartArea'),
    icon: 'AreaChart',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.visitTrend'),
      // 图表配置
      smooth: true,
      stack: false,
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      xAxisData: [
        $t('dashboard-design.months.jan'),
        $t('dashboard-design.months.feb'),
        $t('dashboard-design.months.mar'),
        $t('dashboard-design.months.apr'),
        $t('dashboard-design.months.may'),
        $t('dashboard-design.months.jun'),
        $t('dashboard-design.months.jul'),
        $t('dashboard-design.months.aug'),
        $t('dashboard-design.months.sep'),
        $t('dashboard-design.months.oct'),
        $t('dashboard-design.months.nov'),
        $t('dashboard-design.months.dec'),
      ],
      seriesData: [
        {
          name: '2023',
          data: [
            820, 932, 901, 934, 1290, 1330, 1320, 1450, 1200, 1100, 1350, 1500,
          ],
        },
        {
          name: '2024',
          data: [
            1020, 1132, 1101, 1134, 1490, 1530, 1520, 1650, 1400, 1300, 1550,
            1700,
          ],
        },
      ],
    },
  },
  {
    type: 'chart-radar',
    title: $t('dashboard-design.material.widgets.chartRadar'),
    icon: 'Radar',
    category: 'chart',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.abilityEval'),
      // 图表配置
      shape: 'polygon', // polygon | circle
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858'],
      // 静态数据
      indicators: [
        { name: $t('dashboard-design.material.defaultProps.sales'), max: 100 },
        { name: $t('dashboard-design.material.defaultProps.mgmt'), max: 100 },
        { name: $t('dashboard-design.material.defaultProps.tech'), max: 100 },
        { name: $t('dashboard-design.material.defaultProps.cs'), max: 100 },
        { name: $t('dashboard-design.material.defaultProps.rd'), max: 100 },
        { name: $t('dashboard-design.material.defaultProps.mkt'), max: 100 },
      ],
      seriesData: [
        { name: $t('dashboard-design.material.defaultProps.budget'), value: [85, 90, 80, 70, 75, 88] },
        { name: $t('dashboard-design.material.defaultProps.actual'), value: [90, 85, 95, 80, 70, 92] },
      ],
    },
  },
  {
    type: 'chart-funnel',
    title: $t('dashboard-design.material.widgets.chartFunnel'),
    icon: 'Filter',
    category: 'chart',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.convFunnel'),
      // 图表配置
      sort: 'descending', // descending | ascending | none
      orient: 'vertical', // vertical | horizontal
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      seriesData: [
        { name: $t('dashboard-design.material.defaultProps.visit'), value: 100 },
        { name: $t('dashboard-design.material.defaultProps.consult'), value: 80 },
        { name: $t('dashboard-design.material.defaultProps.intent'), value: 60 },
        { name: $t('dashboard-design.material.defaultProps.order'), value: 40 },
        { name: $t('dashboard-design.material.defaultProps.deal'), value: 20 },
      ],
    },
  },
  {
    type: 'chart-scatter',
    title: $t('dashboard-design.material.widgets.chartScatter'),
    icon: 'ScatterChart',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.dataDist'),
      // 图表配置
      symbolSize: 10,
      // 坐标轴
      xAxisName: $t('dashboard-design.material.defaultProps.height'),
      yAxisName: $t('dashboard-design.material.defaultProps.weight'),
      axisNameLocation: 'end', // start | middle | end
      // 图例
      showLegend: true,
      legendPosition: 'top',
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据 - 每个系列的数据是 [x, y] 坐标数组
      seriesData: [
        {
          name: $t('dashboard-design.material.defaultProps.male'),
          data: [
            [161, 51],
            [167, 59],
            [159, 49],
            [157, 63],
            [155, 53],
            [170, 70],
            [175, 75],
            [180, 80],
            [165, 58],
            [172, 68],
          ],
        },
        {
          name: $t('dashboard-design.material.defaultProps.female'),
          data: [
            [150, 45],
            [155, 50],
            [160, 52],
            [158, 48],
            [162, 55],
            [165, 58],
            [153, 47],
            [168, 60],
            [157, 51],
            [163, 54],
          ],
        },
      ],
    },
  },
  {
    type: 'chart-ring',
    title: $t('dashboard-design.material.widgets.chartRing'),
    icon: 'CircleDot',
    category: 'chart',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.kpiDone'),
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666'],
      // 静态数据 - 多个环形进度
      seriesData: [
        { name: $t('dashboard-design.material.defaultProps.salesVolume'), value: 85, max: 100 },
        { name: $t('dashboard-design.material.defaultProps.orderVolume'), value: 72, max: 100 },
        { name: $t('dashboard-design.material.defaultProps.customerCount'), value: 93, max: 100 },
      ],
    },
  },
  {
    type: 'chart-heatmap',
    title: $t('dashboard-design.material.widgets.chartHeatmap'),
    icon: 'Grid',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.weekVisitHeat'),
      // 静态数据
      xAxisData: [
        $t('dashboard-design.weekdaysShort.mon'),
        $t('dashboard-design.weekdaysShort.tue'),
        $t('dashboard-design.weekdaysShort.wed'),
        $t('dashboard-design.weekdaysShort.thu'),
        $t('dashboard-design.weekdaysShort.fri'),
        $t('dashboard-design.weekdaysShort.sat'),
        $t('dashboard-design.weekdaysShort.sun'),
      ],
      yAxisData: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
      // data: [x索引, y索引, 值]
      seriesData: [
        [0, 0, 5],
        [0, 1, 2],
        [0, 2, 15],
        [0, 3, 28],
        [0, 4, 35],
        [0, 5, 18],
        [1, 0, 3],
        [1, 1, 1],
        [1, 2, 18],
        [1, 3, 32],
        [1, 4, 38],
        [1, 5, 22],
        [2, 0, 4],
        [2, 1, 2],
        [2, 2, 20],
        [2, 3, 30],
        [2, 4, 40],
        [2, 5, 25],
        [3, 0, 6],
        [3, 1, 3],
        [3, 2, 22],
        [3, 3, 35],
        [3, 4, 42],
        [3, 5, 28],
        [4, 0, 8],
        [4, 1, 4],
        [4, 2, 25],
        [4, 3, 38],
        [4, 4, 45],
        [4, 5, 30],
        [5, 0, 15],
        [5, 1, 8],
        [5, 2, 12],
        [5, 3, 20],
        [5, 4, 25],
        [5, 5, 35],
        [6, 0, 12],
        [6, 1, 6],
        [6, 2, 10],
        [6, 3, 18],
        [6, 4, 22],
        [6, 5, 30],
      ],
      minValue: 0,
      maxValue: 50,
    },
  },
  {
    type: 'chart-kline',
    title: $t('dashboard-design.material.widgets.chartKline'),
    icon: 'CandlestickChart',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.stockTrend'),
      // 图表配置
      showMA5: true,
      showMA10: true,
      // 静态数据 - [开盘, 收盘, 最低, 最高]
      xAxisData: [
        '2024/1/2',
        '2024/1/3',
        '2024/1/4',
        '2024/1/5',
        '2024/1/8',
        '2024/1/9',
        '2024/1/10',
        '2024/1/11',
        '2024/1/12',
        '2024/1/15',
      ],
      seriesData: [
        [20, 34, 10, 38],
        [40, 35, 30, 50],
        [31, 38, 33, 44],
        [38, 15, 5, 42],
        [15, 25, 10, 35],
        [25, 32, 20, 38],
        [32, 30, 25, 40],
        [30, 45, 28, 48],
        [45, 50, 40, 55],
        [50, 48, 42, 58],
      ],
    },
  },
  {
    type: 'chart-sankey',
    title: $t('dashboard-design.material.widgets.chartSankey'),
    icon: 'GitBranch',
    category: 'chart',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.trafficSource'),
      // 颜色
      colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'],
      // 静态数据
      nodes: [
        { name: $t('dashboard-design.material.defaultProps.visit') },
        { name: $t('dashboard-design.material.defaultProps.searchEngine') },
        { name: $t('dashboard-design.material.defaultProps.directAccess') },
        { name: $t('dashboard-design.material.defaultProps.consult') },
        { name: $t('dashboard-design.material.defaultProps.intent') },
        { name: $t('dashboard-design.material.defaultProps.order') },
        { name: $t('dashboard-design.material.defaultProps.deal') },
      ],
      links: [
        { source: $t('dashboard-design.material.defaultProps.visit'), target: $t('dashboard-design.material.defaultProps.searchEngine'), value: 500 },
        { source: $t('dashboard-design.material.defaultProps.visit'), target: $t('dashboard-design.material.defaultProps.directAccess'), value: 300 },
        { source: $t('dashboard-design.material.defaultProps.visit'), target: $t('dashboard-design.material.defaultProps.consult'), value: 200 },
        { source: $t('dashboard-design.material.defaultProps.searchEngine'), target: $t('dashboard-design.material.defaultProps.intent'), value: 300 },
        { source: $t('dashboard-design.material.defaultProps.directAccess'), target: $t('dashboard-design.material.defaultProps.intent'), value: 200 },
        { source: $t('dashboard-design.material.defaultProps.consult'), target: $t('dashboard-design.material.defaultProps.order'), value: 150 },
        { source: $t('dashboard-design.material.defaultProps.order'), target: $t('dashboard-design.material.defaultProps.deal'), value: 400 },
      ],
    },
  },
  // 列表
  {
    type: 'todo-list',
    title: $t('dashboard-design.material.widgets.todoList'),
    icon: 'CheckSquare',
    category: 'list',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.todoTitle'),
      items: [
        { id: '1', title: $t('dashboard-design.material.defaultProps.todoItem1'), done: false, priority: 'high' },
        { id: '2', title: $t('dashboard-design.material.defaultProps.todoItem2'), done: true, priority: 'medium' },
        { id: '3', title: $t('dashboard-design.material.defaultProps.todoItem3'), done: false, priority: 'low' },
      ],
    },
  },
  {
    type: 'notice-list',
    title: $t('dashboard-design.material.widgets.noticeList'),
    icon: 'Bell',
    category: 'list',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.latestNotice'),
      limit: 5,
    },
  },
  {
    type: 'announcement-list',
    title: $t('dashboard-design.material.widgets.announcementList'),
    icon: 'Megaphone',
    category: 'list',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.latestAnnouncement'),
      limit: 5,
    },
  },
  {
    type: 'ranking-list',
    title: $t('dashboard-design.material.widgets.rankingList'),
    icon: 'Award',
    category: 'list',
    defaultW: 4,
    defaultH: 4,
    minW: 3,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.salesRanking'),
      items: [
        { rank: 1, name: '张三', value: 12_000 },
        { rank: 2, name: '李四', value: 10_000 },
        { rank: 3, name: '王五', value: 8000 },
        { rank: 4, name: '赵六', value: 6000 },
        { rank: 5, name: '钱七', value: 4000 },
      ],
    },
  },
  // 快捷入口（归类到列表）
  {
    type: 'quick-links',
    title: $t('dashboard-design.material.widgets.quickLinks'),
    icon: 'Grid',
    category: 'list',
    defaultW: 4,
    defaultH: 3,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.attribute.widget.quickLinks.title') || '快捷入口',
      columns: 4,
      rows: 2,
      menus: [],
    },
  },
  // 内容
  {
    type: 'welcome-card',
    title: $t('dashboard-design.material.widgets.welcomeCard'),
    icon: 'Smile',
    category: 'widget',
    defaultW: 6,
    defaultH: 2,
    minW: 4,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.welcomeTitle'),
      subtitle: $t('dashboard-design.material.defaultProps.welcomeSubtitle'),
      showTime: true,
      showWeather: false,
    },
  },
  {
    type: 'calendar',
    title: $t('dashboard-design.material.widgets.calendar'),
    icon: 'Calendar',
    category: 'widget',
    defaultW: 4,
    defaultH: 5,
    minW: 3,
    minH: 4,
    defaultProps: {
      title: $t('dashboard-design.material.widgets.calendar'),
      showLunar: false,
    },
  },
  // 工具组件
  {
    type: 'countdown',
    title: $t('dashboard-design.material.widgets.countdown'),
    icon: 'Timer',
    category: 'widget',
    defaultW: 3,
    defaultH: 2,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.countdownTitle'),
      targetTime: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7天后
      showDays: true,
      showHours: true,
      showMinutes: true,
      showSeconds: true,
      finishedText: $t('dashboard-design.attribute.widget.countdown.finishedTextPlaceholder'),
    },
  },
  {
    type: 'clock',
    title: $t('dashboard-design.material.widgets.clock'),
    icon: 'Clock',
    category: 'widget',
    defaultW: 3,
    defaultH: 2,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: '',
      showDate: true,
      showSeconds: true,
      format24: true,
      timezone: 'local', // local, UTC, Asia/Shanghai 等
    },
  },
  {
    type: 'weather',
    title: $t('dashboard-design.material.widgets.weather'),
    icon: 'CloudSun',
    category: 'widget',
    defaultW: 3,
    defaultH: 2,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.todayWeather'),
      city: '北京',
      temperature: 25,
      weather: '晴',
      humidity: 45,
      wind: '东北风 3级',
      icon: 'sunny', // sunny, cloudy, rainy, snowy, foggy
    },
  },
  {
    type: 'image-carousel',
    title: $t('dashboard-design.material.widgets.imageCarousel'),
    icon: 'Images',
    category: 'widget',
    defaultW: 6,
    defaultH: 3,
    minW: 3,
    minH: 2,
    defaultProps: {
      title: '',
      images: [
        {
          url: 'https://picsum.photos/800/400?random=1',
          title: $t('dashboard-design.material.defaultProps.imageTitle') + ' 1',
          link: '',
        },
        {
          url: 'https://picsum.photos/800/400?random=2',
          title: $t('dashboard-design.material.defaultProps.imageTitle') + ' 2',
          link: '',
        },
        {
          url: 'https://picsum.photos/800/400?random=3',
          title: $t('dashboard-design.material.defaultProps.imageTitle') + ' 3',
          link: '',
        },
      ],
      autoplay: true,
      interval: 3000,
      showIndicator: true,
      showArrow: true,
    },
  },
  {
    type: 'data-table',
    title: $t('dashboard-design.material.widgets.dataTable'),
    icon: 'Table',
    category: 'list',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.dataList'),
      columns: [
        { prop: 'name', label: $t('dashboard-design.attribute.placeholder.name'), width: 120 },
        { prop: 'value', label: $t('dashboard-design.attribute.fieldLabels.value'), width: 100 },
        { prop: 'status', label: $t('dashboard-design.attribute.status'), width: 80 },
        { prop: 'time', label: $t('dashboard-design.attribute.clock.timezone'), width: 150 },
      ],
      data: [
        {
          name: $t('dashboard-design.material.defaultProps.itemName') + ' A',
          value: 1234,
          status: $t('dashboard-design.widgets.dataTable.status.normal'),
          time: '2024-01-01 10:00',
        },
        {
          name: $t('dashboard-design.material.defaultProps.itemName') + ' B',
          value: 5678,
          status: $t('dashboard-design.widgets.dataTable.status.warning'),
          time: '2024-01-02 11:00',
        },
        {
          name: $t('dashboard-design.material.defaultProps.itemName') + ' C',
          value: 9012,
          status: $t('dashboard-design.widgets.dataTable.status.normal'),
          time: '2024-01-03 12:00',
        },
        {
          name: $t('dashboard-design.material.defaultProps.itemName') + ' D',
          value: 3456,
          status: $t('dashboard-design.widgets.dataTable.status.error'),
          time: '2024-01-04 13:00',
        },
      ],
      stripe: true,
      border: false,
      showIndex: false,
      size: 'default',
    },
  },
  {
    type: 'iframe',
    title: $t('dashboard-design.material.widgets.iframe'),
    icon: 'Globe',
    category: 'widget',
    defaultW: 6,
    defaultH: 4,
    minW: 3,
    minH: 2,
    defaultProps: {
      title: $t('dashboard-design.material.defaultProps.externalPage'),
      url: 'https://www.example.com',
      showBorder: true,
      allowFullscreen: true,
    },
  },
  {
    type: 'video-player',
    title: $t('dashboard-design.material.widgets.videoPlayer'),
    icon: 'Video',
    category: 'widget',
    defaultW: 6,
    defaultH: 4,
    minW: 4,
    minH: 3,
    defaultProps: {
      title: '',
      url: 'https://www.w3schools.com/html/mov_bbb.mp4',
      poster: '',
      autoplay: false,
      loop: false,
      muted: false,
      controls: true,
    },
  },
  {
    type: 'image',
    title: $t('dashboard-design.material.widgets.image'),
    icon: 'Image',
    category: 'widget',
    defaultW: 4,
    defaultH: 3,
    minW: 2,
    minH: 2,
    defaultProps: {
      title: '',
      src: 'https://picsum.photos/400/300',
      alt: $t('dashboard-design.attribute.widget.image.title'),
      fit: 'cover',
      lazy: true,
      previewSrcList: [],
      zIndex: 2000,
      hideOnClickModal: false,
    },
  },
];

export const useDashboardDesignStore = defineStore('dashboard-design', () => {
  // 当前选中的 widget
  const activeId = ref<null | string>(null);

  // 仪表盘配置
  const dashboardConfig = ref<DashboardConfig>({
    id: uuidv4(),
    name: $t('dashboard-design.material.defaultProps.myDashboard'),
    columns: 12,
    rowHeight: 50,
    margin: [12, 12],
    widgets: [],
  });

  // 历史记录
  const history = ref<string[]>([]);
  const historyIndex = ref(-1);
  const isTimeTravel = ref(false);

  // 剪贴板状态
  const clipboard = ref<DashboardWidget | null>(null);

  // 拖拽状态
  const isDragging = ref(false);

  // 预览模式
  const isPreview = ref(false);

  // 记录快照
  const recordSnapshot = () => {
    if (isTimeTravel.value) return;

    if (historyIndex.value < history.value.length - 1) {
      history.value.splice(historyIndex.value + 1);
    }

    history.value.push(JSON.stringify(dashboardConfig.value));
    historyIndex.value = history.value.length - 1;

    if (history.value.length > 30) {
      history.value.shift();
      historyIndex.value--;
    }
  };

  // 不自动监听，改为手动记录快照，避免无限循环

  const canUndo = computed(() => historyIndex.value > 0);
  const canRedo = computed(() => historyIndex.value < history.value.length - 1);

  const undo = () => {
    if (!canUndo.value) return;

    isTimeTravel.value = true;
    historyIndex.value--;
    const snapshot = history.value[historyIndex.value];
    if (snapshot) {
      dashboardConfig.value = JSON.parse(snapshot);
    }

    nextTick(() => {
      isTimeTravel.value = false;
    });
  };

  const redo = () => {
    if (!canRedo.value) return;

    isTimeTravel.value = true;
    historyIndex.value++;
    const snapshot = history.value[historyIndex.value];
    if (snapshot) {
      dashboardConfig.value = JSON.parse(snapshot);
    }

    nextTick(() => {
      isTimeTravel.value = false;
    });
  };

  // 设置当前选中
  const setActive = (id: null | string) => {
    activeId.value = id;
  };

  // 获取当前选中的 widget
  const activeWidget = computed(() => {
    if (!activeId.value) return null;
    return (
      dashboardConfig.value.widgets.find((w) => w.id === activeId.value) || null
    );
  });

  // 计算下一个 widget 的 y 位置
  const getNextY = () => {
    if (dashboardConfig.value.widgets.length === 0) return 0;
    let maxY = 0;
    for (const w of dashboardConfig.value.widgets) {
      const bottom = w.y + w.h;
      if (bottom > maxY) maxY = bottom;
    }
    return maxY;
  };

  // 添加 widget
  const addWidget = (
    material: WidgetMaterial,
    position?: { x: number; y: number },
  ) => {
    const id = uuidv4();
    const widget: DashboardWidget = {
      id,
      i: id,
      type: material.type,
      x: position?.x ?? 0,
      y: position?.y ?? getNextY(),
      w: material.defaultW,
      h: material.defaultH,
      minW: material.minW,
      minH: material.minH,
      title: material.title,
      props: JSON.parse(JSON.stringify(material.defaultProps)),
    };

    dashboardConfig.value.widgets.push(widget);
    activeId.value = id;
    recordSnapshot();
  };

  // 删除 widget
  const deleteWidget = (id: string) => {
    const index = dashboardConfig.value.widgets.findIndex((w) => w.id === id);
    if (index !== -1) {
      dashboardConfig.value.widgets.splice(index, 1);
      if (activeId.value === id) {
        activeId.value = null;
      }
      recordSnapshot();
    }
  };

  // 复制 widget（直接复制并粘贴）
  const copyWidget = (id: string) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (!widget) return;

    const newId = uuidv4();
    const newWidget: DashboardWidget = {
      ...JSON.parse(JSON.stringify(widget)),
      id: newId,
      i: newId,
      y: widget.y + widget.h,
    };

    dashboardConfig.value.widgets.push(newWidget);
    activeId.value = newId;
    recordSnapshot();
  };

  // 复制到剪贴板
  const copyToClipboard = (id: string) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (widget) {
      clipboard.value = JSON.parse(JSON.stringify(widget));
    }
  };

  // 从剪贴板粘贴
  const pasteFromClipboard = () => {
    if (!clipboard.value) return false;

    const newId = uuidv4();
    const newWidget: DashboardWidget = {
      ...JSON.parse(JSON.stringify(clipboard.value)),
      id: newId,
      i: newId,
      y: getNextY(),
    };

    dashboardConfig.value.widgets.push(newWidget);
    activeId.value = newId;
    recordSnapshot();
    return true;
  };

  // 检查剪贴板是否有内容
  const hasClipboard = computed(() => clipboard.value !== null);

  // 更新 widget 属性
  const updateWidgetProps = (id: string, props: Record<string, any>) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (widget) {
      widget.props = { ...widget.props, ...props };
    }
  };

  // 更新 widget 标题
  const updateWidgetTitle = (id: string, title: string) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (widget) {
      widget.title = title;
    }
  };

  // 更新 widget 数据源配置
  const updateWidgetDataSource = (id: string, dataSource: DataSourceConfig) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (widget) {
      widget.dataSource = { ...dataSource };
      recordSnapshot();
    }
  };

  // 更新 widget 样式配置
  const updateWidgetStyle = (id: string, style: Partial<WidgetStyle>) => {
    const widget = dashboardConfig.value.widgets.find((w) => w.id === id);
    if (widget) {
      widget.style = { ...defaultWidgetStyle, ...widget.style, ...style };
      recordSnapshot();
    }
  };

  // 更新布局
  const updateLayout = (
    layout: { h: number; i: string; w: number; x: number; y: number }[],
  ) => {
    for (const item of layout) {
      const widget = dashboardConfig.value.widgets.find((w) => w.i === item.i);
      if (widget) {
        widget.x = item.x;
        widget.y = item.y;
        widget.w = item.w;
        widget.h = item.h;
      }
    }
  };

  // 设置拖拽状态
  const setDragging = (val: boolean) => {
    isDragging.value = val;
  };

  // 设置预览模式
  const setPreview = (val: boolean) => {
    isPreview.value = val;
  };

  // 清空画布
  const clearCanvas = () => {
    dashboardConfig.value.widgets = [];
    activeId.value = null;
    recordSnapshot();
  };

  // 移动 widget 层级 - 上移一层
  const moveWidgetUp = (id: string) => {
    const widgets = dashboardConfig.value.widgets;
    const index = widgets.findIndex((w) => w.id === id);
    if (index > 0) {
      [widgets[index - 1], widgets[index]] = [
        widgets[index]!,
        widgets[index - 1]!,
      ];
      recordSnapshot();
    }
  };

  // 移动 widget 层级 - 下移一层
  const moveWidgetDown = (id: string) => {
    const widgets = dashboardConfig.value.widgets;
    const index = widgets.findIndex((w) => w.id === id);
    if (index < widgets.length - 1) {
      [widgets[index], widgets[index + 1]] = [
        widgets[index + 1]!,
        widgets[index]!,
      ];
      recordSnapshot();
    }
  };

  // 移动 widget 层级 - 置顶
  const moveWidgetToTop = (id: string) => {
    const widgets = dashboardConfig.value.widgets;
    const index = widgets.findIndex((w) => w.id === id);
    if (index > 0) {
      const [widget] = widgets.splice(index, 1);
      widgets.unshift(widget!);
      recordSnapshot();
    }
  };

  // 移动 widget 层级 - 置底
  const moveWidgetToBottom = (id: string) => {
    const widgets = dashboardConfig.value.widgets;
    const index = widgets.findIndex((w) => w.id === id);
    if (index < widgets.length - 1) {
      const [widget] = widgets.splice(index, 1);
      widgets.push(widget!);
      recordSnapshot();
    }
  };

  // 导出配置
  const exportConfig = () => {
    return JSON.stringify(dashboardConfig.value, null, 2);
  };

  // 导入配置
  const importConfig = (json: string) => {
    try {
      const config = JSON.parse(json);
      dashboardConfig.value = config;
      activeId.value = null;
      return true;
    } catch {
      return false;
    }
  };

  // 更新仪表盘基础配置
  const updateDashboardConfig = (config: Partial<DashboardConfig>) => {
    Object.assign(dashboardConfig.value, config);
  };

  return {
    activeId,
    activeWidget,
    dashboardConfig,
    isDragging,
    isPreview,
    canUndo,
    canRedo,
    hasClipboard,
    setActive,
    addWidget,
    deleteWidget,
    copyWidget,
    copyToClipboard,
    pasteFromClipboard,
    updateWidgetProps,
    updateWidgetTitle,
    updateWidgetDataSource,
    updateWidgetStyle,
    updateLayout,
    setDragging,
    setPreview,
    clearCanvas,
    exportConfig,
    importConfig,
    updateDashboardConfig,
    moveWidgetUp,
    moveWidgetDown,
    moveWidgetToTop,
    moveWidgetToBottom,
    undo,
    redo,
  };
});
