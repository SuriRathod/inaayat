import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os

# Configuration
WORDPRESS_URL = "https://surirathoreblog.wordpress.com"
POETRY_PAGE_URL = f"{WORDPRESS_URL}/poetry-blog/"
OUTPUT_DIR = "src/content/poems"

def clean_filename(title):
    """Convert title to URL-friendly slug"""
    # Remove special characters and convert to lowercase
    slug = title.lower()
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def extract_date_from_url(url):
    """Extract date from WordPress URL format: /YYYY/MM/DD/title/"""
    match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))
    return datetime.now()

def get_poem_urls():
    """Scrape the poetry listing page to get all poem URLs"""
    print(f"Fetching poem list from: {POETRY_PAGE_URL}")
    response = requests.get(POETRY_PAGE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    poem_urls = []
    # Find all article links
    articles = soup.find_all('article')
    
    for article in articles:
        link = article.find('a', href=True)
        if link and '/poetry-blog/' not in link['href']:  # Skip the category page itself
            poem_urls.append(link['href'])
    
    # Remove duplicates and return
    return list(set(poem_urls))

def scrape_poem(url):
    """Scrape individual poem page and extract content"""
    print(f"Scraping: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract title
    title_elem = soup.find('h1', class_='entry-title')
    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
    
    # Extract date from URL
    date = extract_date_from_url(url)
    
    # Extract poem content
    content_div = soup.find('div', class_='entry-content')
    
    if not content_div:
        print(f"  WARNING: Could not find content for {title}")
        return None
    
    # Extract featured image - it's in post-thumbnail, not entry-content
    image_url = None
    thumbnail = soup.find('img', class_='wp-post-image')
    if not thumbnail:
        thumbnail = soup.find(class_='post-thumbnail')
    
    if thumbnail:
        if thumbnail.name == 'img':
            image_url = thumbnail.get('src')
        else:
            # If it's a container, find img inside
            img_elem = thumbnail.find('img')
            if img_elem:
                image_url = img_elem.get('src')
        
        # Clean up the URL - remove WordPress resizing parameters
        if image_url and '?' in image_url:
            image_url = image_url.split('?')[0]
        
        print(f"  Image found: {image_url}")
    else:
        print(f"  No featured image")
    
    # Skip phrases - unwanted WordPress elements
    skip_phrases = [
        "Subscribe to Blog",
        "Enter your email",
        "Email Address:",
        "Join 447 other subscribers",
        "Follow",
        "Sign me up"
    ]
    
    # Get all paragraphs and process
    poem_stanzas = []
    for p in content_div.find_all('p'):
        # First convert <br> tags to newlines before extracting text
        for br in p.find_all('br'):
            br.replace_with('\n')
        
        text = p.get_text()
        
        # Check if this paragraph should be skipped
        should_skip = any(phrase in text for phrase in skip_phrases)
        
        if text.strip() and not should_skip:
            # Split by newlines and add <br> tags
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:  # Only add if there are actual lines
                stanza = '<br>\n'.join(lines)
                poem_stanzas.append(stanza)
    
    # Wrap each stanza in <p> tags and join them
    poem_content = '\n\n'.join([f'<p>{stanza}</p>' for stanza in poem_stanzas])
    
    # Create excerpt (first 100 chars)
    excerpt = poem_content[:100].replace('<br>', ' ').replace('\n', ' ')
    if len(poem_content) > 100:
        excerpt += "..."
    
    return {
        'title': title,
        'date': date,
        'excerpt': excerpt,
        'content': poem_content,
        'slug': clean_filename(title),
        'image': image_url
    }

def create_markdown_file(poem):
    """Create a markdown file for the poem"""
    # Get the absolute path to ensure it works on Windows
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    output_path = os.path.join(project_dir, OUTPUT_DIR)
    
    # Ensure output directory exists
    os.makedirs(output_path, exist_ok=True)
    
    filename = os.path.join(output_path, f"{poem['slug']}.md")
    
    # Create frontmatter
    image_line = f'image: "{poem["image"]}"' if poem.get('image') else ''
    frontmatter = f"""---
title: "{poem['title']}"
date: {poem['date'].strftime('%Y-%m-%d')}
excerpt: "{poem['excerpt']}"
{image_line}
---

{poem['content']}
"""
    
    # Write file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    print(f"  ✓ Created: {filename}")

def main():
    """Main migration function"""
    print("=" * 60)
    print("WordPress Poetry Migration Script")
    print("=" * 60)
    print()
    
    # Step 1: Get all poem URLs
    poem_urls = get_poem_urls()
    print(f"\nFound {len(poem_urls)} poems to migrate\n")
    
    # Step 2: Process each poem
    success_count = 0
    failed_count = 0
    
    for i, url in enumerate(poem_urls, 1):
        print(f"[{i}/{len(poem_urls)}] Processing...")
        try:
            poem = scrape_poem(url)
            if poem:
                create_markdown_file(poem)
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            failed_count += 1
        print()
    
    # Summary
    print("=" * 60)
    print(f"Migration Complete!")
    print(f"  Success: {success_count}")
    print(f"  Failed:  {failed_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()