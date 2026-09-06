import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);

function getElementPlusComponentsDir(): string {
  const elementPlusPkg = require.resolve('element-plus/package.json');
  return path.join(path.dirname(elementPlusPkg), 'es/components');
}

/**
 * Pre-bundle Element Plus sub-modules to avoid Vite re-optimizing on each page navigation.
 */
export function getElementPlusOptimizeDeps(): string[] {
  const componentsDir = getElementPlusComponentsDir();
  const components = fs
    .readdirSync(componentsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  const deps = new Set<string>([
    'element-plus',
    'element-plus/es',
    '@element-plus/icons-vue',
    'element-plus/es/components/base/style/css',
    'element-plus/es/components/message/style/css',
    'element-plus/es/components/message-box/style/css',
    'element-plus/es/components/notification/style/css',
    'element-plus/es/components/loading/style/css',
    'element-plus/es/locale/lang/zh-cn',
    'element-plus/es/locale/lang/en',
    'element-plus/es/locale/lang/zh-tw',
  ]);

  for (const component of components) {
    const componentDir = path.join(componentsDir, component);
    if (fs.existsSync(path.join(componentDir, 'index.mjs'))) {
      deps.add(`element-plus/es/components/${component}/index`);
    }

    const styleCssDir = path.join(componentDir, 'style');
    if (fs.existsSync(path.join(styleCssDir, 'css.mjs'))) {
      deps.add(`element-plus/es/components/${component}/style/css`);
    }
  }

  return [...deps];
}
