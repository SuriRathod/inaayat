import { defineCollection, z } from 'astro:content';

const poemsCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.date(),
    excerpt: z.string(),
    image: z.string().optional(),
  }),
});

const storiesCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.date(),
    excerpt: z.string(),
    image: z.string().optional(),
    readTime: z.string().optional(),
  }),
});

export const collections = {
  poems: poemsCollection,
  stories: storiesCollection,
};