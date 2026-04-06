import { getCollection } from 'astro:content';

export async function GET() {
  const allPoems = await getCollection('poems');
  const allStories = await getCollection('stories');

  const searchIndex = [
    ...allPoems.map(poem => ({
      type: 'poems',
      slug: poem.slug,
      title: poem.data.title,
      excerpt: poem.data.excerpt.replace(/<[^>]*>/g, ''),
      date: poem.data.date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    })),
    ...allStories.map(story => ({
      type: 'stories',
      slug: story.slug,
      title: story.data.title,
      excerpt: story.data.excerpt.replace(/<[^>]*>/g, ''),
      date: story.data.date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    }))
  ];

  return new Response(JSON.stringify(searchIndex), {
    headers: {
      'Content-Type': 'application/json',
    },
  });
}