import { defineConfig } from '@vben/vite-config';

import ElementPlus from 'unplugin-element-plus/vite';

import { getElementPlusOptimizeDeps } from './build/element-plus-optimize-deps';

export default defineConfig(async ({ command }) => {
  const isDev = command === 'serve';

  return {
    application: {},
    vite: {
      optimizeDeps: {
        holdUntilCrawlEnd: true,
        include: getElementPlusOptimizeDeps(),
      },
      resolve: {
        dedupe: [
          '@tiptap/core',
          '@tiptap/pm',
          'prosemirror-model',
          'prosemirror-state',
          'prosemirror-view',
          'prosemirror-transform',
          'prosemirror-keymap',
          'prosemirror-commands',
          'prosemirror-schema-list',
          'prosemirror-inputrules',
          'prosemirror-dropcursor',
          'prosemirror-gapcursor',
          'prosemirror-history',
          'prosemirror-tables',
        ],
      },
      plugins: [
        ElementPlus({
          format: 'esm',
          // 开发环境使用全量样式，避免按需 CSS 触发 Vite 反复预构建与 reloading
          importStyle: isDev ? false : 'css',
        }),
      ],
      server: {
        proxy: {
          '/basic-api': {
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/basic-api/, ''),
            // mock代理目标地址
            target: 'http://localhost:8000',
            ws: true,
          },
          '/ws': {
            changeOrigin: true,
            target: 'ws://localhost:8000',
            ws: true,
          },
        },
      },
    },
  };
});
