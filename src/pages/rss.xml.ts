import { getCollection } from 'astro:content';

function escapeXml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

export async function GET() {
  const allPoems = await getCollection('poems');
  const allStories = await getCollection('stories');
  const allContent = [...allPoems, ...allStories].sort(
    (a, b) => b.data.date.valueOf() - a.data.date.valueOf()
  );

  const siteUrl = 'https://inaayat.art';
  const siteTitle = 'Inaayat — Poetry & Reflections';
  const siteDescription = 'An expression of reality — Words woven from moments of reflection';

  const rssContent = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${escapeXml(siteTitle)}</title>
    <description>${escapeXml(siteDescription)}</description>
    <link>${siteUrl}</link>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml" />
    <language>en</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${allContent
      .map(item => {
        const type = item.collection === 'poems' ? 'poems' : 'stories';
        const url = `${siteUrl}/${type}/${item.slug}`;
        const excerpt = item.data.excerpt.replace(/<[^>]*>/g, '').substring(0, 200);

        return `
    <item>
      <title>${escapeXml(item.data.title)}</title>
      <link>${url}</link>
      <guid>${url}</guid>
      <pubDate>${item.data.date.toUTCString()}</pubDate>
      <description><![CDATA[${excerpt}...]]></description>
    </item>`;
      })
      .join('')}
  </channel>
</rss>`;

  return new Response(rssContent, {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
}