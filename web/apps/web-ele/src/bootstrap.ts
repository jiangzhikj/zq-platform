import { createApp, watchEffect } from 'vue';

import { registerAccessDirective } from '@vben/access';
import { registerLoadingDirective } from '@vben/common-ui';
import { preferences } from '@vben/preferences';
import { initStores } from '@vben/stores';
import '@vben/styles';
import '@vben/styles/ele';

import { useTitle } from '@vueuse/core';
import ElementPlus from 'element-plus';
import { ElLoading } from 'element-plus';

import { $t, setupI18n } from '#/locales';

import { initComponentAdapter } from './adapter/component';
import { initSetupVbenForm, useVbenForm } from './adapter/form';
import App from './app.vue';
import { setupZqTable } from './components/zq-table';
import { router } from './router';

async function bootstrap(namespace: string) {
  // 开发环境全量引入 Element Plus 样式，避免按需 CSS 导致 Vite 反复 reloading
  if (import.meta.env.DEV) {
    await import('element-plus/dist/index.css');
  }

  // 初始化组件适配器
  await initComponentAdapter();

  // 初始化表单组件
  await initSetupVbenForm();

  // 初始化 ZqTable (注入 form)
  setupZqTable({
    useVbenForm,
  });

  // // 设置弹窗的默认配置
  // setDefaultModalProps({
  //   fullscreenButton: false,
  // });
  // // 设置抽屉的默认配置
  // setDefaultDrawerProps({
  //   zIndex: 2000,
  // });
  const app = createApp(App);

  app.use(ElementPlus);

  // 注册Element Plus提供的v-loading指令
  app.directive('loading', ElLoading.directive);

  // 注册Vben提供的v-loading和v-spinning指令
  registerLoadingDirective(app, {
    loading: false, // Vben提供的v-loading指令和Element Plus提供的v-loading指令二选一即可，此处false表示不注册Vben提供的v-loading指令
    spinning: 'spinning',
  });

  // 国际化 i18n 配置
  await setupI18n(app);

  // 配置 pinia-tore
  await initStores(app, { namespace });

  // 初始化跨tab的token同步机制
  const { useAccessStore } = await import('@vben/stores');
  const accessStore = useAccessStore();

  // 从共享存储加载 token（主应用和子应用共享）
  const SHARED_TOKEN_KEY = 'vben-shared-auth-tokens';
  try {
    const stored = localStorage.getItem(SHARED_TOKEN_KEY);
    if (stored) {
      const tokens = JSON.parse(stored);
      console.log('[Bootstrap] 从共享存储加载token:', {
        hasAccessToken: !!tokens.accessToken,
        hasRefreshToken: !!tokens.refreshToken,
      });
      // 直接修改 $state，避免触发 saveSharedTokens（因为数据本来就是从 localStorage 读取的）
      if (tokens.accessToken) {
        accessStore.$state.accessToken = tokens.accessToken;
      }
      if (tokens.refreshToken) {
        accessStore.$state.refreshToken = tokens.refreshToken;
      }
    }
  } catch (error) {
    console.error('[Bootstrap] 加载共享token失败:', error);
  }

  // 监听 localStorage 的变化（跨tab通信）
  // Token 使用固定 key 'vben-shared-auth-tokens' 存储，主应用和子应用共享
  window.addEventListener('storage', (event) => {
    // 只处理共享的 token key 的变化
    if (event.key === 'vben-shared-auth-tokens') {
      try {
        // 当其他 tab 更新了 token，同步到当前 tab 的 Pinia Store
        const newValue = event.newValue ? JSON.parse(event.newValue) : null;

        if (newValue) {
          // 直接修改 $state，避免触发 saveSharedTokens 导致循环
          if (
            newValue.accessToken !== undefined &&
            newValue.accessToken !== accessStore.accessToken
          ) {
            console.log(
              '[跨Tab同步] 检测到其他tab更新了accessToken，同步中...',
            );
            accessStore.$state.accessToken = newValue.accessToken;
          }

          if (
            newValue.refreshToken !== undefined &&
            newValue.refreshToken !== accessStore.refreshToken
          ) {
            console.log(
              '[跨Tab同步] 检测到其他tab更新了refreshToken，同步中...',
            );
            accessStore.$state.refreshToken = newValue.refreshToken;
          }
        } else {
          // token 被清除（退出登录），同步清除当前 tab 的 token
          if (accessStore.accessToken) {
            console.log('[跨Tab同步] 检测到其他tab退出登录，同步清除token...');
            accessStore.$state.accessToken = null;
            accessStore.$state.refreshToken = null;
          }
        }
      } catch (error) {
        console.error('[跨Tab同步] 解析localStorage数据失败:', error);
      }
    }
  });

  // 初始化应用上下文（从 URL 参数中获取 appCode）
  const { useAppContextStore } = await import('#/store/app-context');
  const appContextStore = useAppContextStore();
  await appContextStore.initFromUrl();

  // 安装权限指令
  registerAccessDirective(app);

  // 初始化 tippy
  const { initTippy } = await import('@vben/common-ui/es/tippy');
  initTippy(app);

  // 配置路由及路由守卫
  app.use(router);

  // 配置Motion插件
  const { MotionPlugin } = await import('@vben/plugins/motion');
  app.use(MotionPlugin);

  // 动态更新标题
  watchEffect(() => {
    if (preferences.app.dynamicTitle) {
      const routeTitle = router.currentRoute.value.meta?.title;
      const pageTitle =
        (routeTitle ? `${$t(routeTitle)} - ` : '') + preferences.app.name;
      useTitle(pageTitle);
    }
  });

  app.mount('#app');
}

export { bootstrap };
