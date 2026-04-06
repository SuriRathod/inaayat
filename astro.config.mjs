import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  site: 'https://surirathod.github.io',
  base: '/inaayat',
  trailingSlash: 'never',
});