import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [tailwind()],
  site: 'https://inaayat.art',
  base: '/',
  trailingSlash: 'always',
});