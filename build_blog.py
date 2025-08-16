#!/usr/bin/env python3
"""
Blog Builder Script
Converts markdown blog posts to HTML using a template
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    if not content.startswith('---'):
        return {}, content
    
    try:
        # Find the end of frontmatter
        end_match = re.search(r'\n---\n', content)
        if not end_match:
            return {}, content
        
        frontmatter_text = content[4:end_match.start()]
        markdown_content = content[end_match.end():]
        
        # Parse frontmatter (simple YAML parser)
        frontmatter = {}
        for line in frontmatter_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                
                # Handle arrays
                if value.startswith('[') and value.endswith(']'):
                    value = [item.strip().strip('"').strip("'") for item in value[1:-1].split(',')]
                
                frontmatter[key] = value
        
        return frontmatter, markdown_content
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        return {}, content

def markdown_to_html(markdown_content):
    """Convert markdown to HTML with strategic ad placement"""
    lines = markdown_content.split('\n')
    result_lines = []
    in_list = False
    in_code_block = False
    in_table = False
    code_block_content = []
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                # Starting code block
                in_code_block = True
                code_block_content = []
                # Extract language if present
                lang = line.strip()[3:].strip()
                i += 1
                continue
            else:
                # Ending code block
                in_code_block = False
                # Join code content preserving original formatting
                code_html = '\n'.join(code_block_content)
                result_lines.append(f'<pre><code>{code_html}</code></pre>')
                i += 1
                continue
        
        if in_code_block:
            code_block_content.append(line)
            i += 1
            continue
        
        # Handle tables
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            
            # Clean up table row
            cells = [cell.strip() for cell in line.strip().split('|')[1:-1]]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            # End of table - process accumulated rows
            if table_rows:
                result_lines.append('<table>')
                
                # First row is header
                if table_rows:
                    result_lines.append('<thead><tr>')
                    for cell in table_rows[0]:
                        processed_cell = process_inline_formatting(cell)
                        result_lines.append(f'<th>{processed_cell}</th>')
                    result_lines.append('</tr></thead>')
                
                # Skip separator row (usually second row with dashes)
                start_row = 2 if len(table_rows) > 1 and all('-' in cell for cell in table_rows[1]) else 1
                
                # Body rows
                if len(table_rows) > start_row:
                    result_lines.append('<tbody>')
                    for row in table_rows[start_row:]:
                        result_lines.append('<tr>')
                        for cell in row:
                            processed_cell = process_inline_formatting(cell)
                            result_lines.append(f'<td>{processed_cell}</td>')
                        result_lines.append('</tr>')
                    result_lines.append('</tbody>')
                
                result_lines.append('</table>')
            
            in_table = False
            # Continue processing current line as normal content (don't increment i yet)
        
        if not in_table:
            # Handle headers
            if line.startswith('### '):
                header_text = process_inline_formatting(line[4:])
                result_lines.append(f'<h3>{header_text}</h3>')
            elif line.startswith('## '):
                header_text = process_inline_formatting(line[3:])
                result_lines.append(f'<h2>{header_text}</h2>')
            elif line.startswith('# '):
                header_text = process_inline_formatting(line[2:])
                result_lines.append(f'<h1>{header_text}</h1>')
            # Handle lists
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                item = line.strip()[2:]
                # Process inline formatting in list items
                item = process_inline_formatting(item)
                result_lines.append(f'<li>{item}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                
                # Handle empty lines
                if not line.strip():
                    result_lines.append('')
                # Handle horizontal rules
                elif line.strip() == '---':
                    result_lines.append('<hr>')
                # Handle paragraphs
                elif line.strip() and not line.strip().startswith('<'):
                    processed_line = process_inline_formatting(line.strip())
                    result_lines.append(f'<p>{processed_line}</p>')
                else:
                    result_lines.append(line)
        
        i += 1
    
    # Close any remaining open tags
    if in_list:
        result_lines.append('</ul>')
    
    # Insert in-article ads at strategic positions
    html_with_ads = insert_in_article_ads('\n'.join(result_lines))
    
    return html_with_ads

def process_inline_formatting(text):
    """Process inline markdown formatting like bold, italic, code, links"""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

def insert_in_article_ads(html_content):
    """Insert Google AdSense in-article ads at strategic positions"""
    
    # In-article ad code
    in_article_ad = '''
<div class="ad-container" style="margin: 30px 0; text-align: center;">
    <ins class="adsbygoogle"
         style="display:block; text-align:center;"
         data-ad-layout="in-article"
         data-ad-format="fluid"
         data-ad-client="ca-pub-6705222517983610"
         data-ad-slot="1879717900"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</div>
'''
    
    # Split content into sections based on h2 headers
    sections = re.split(r'(<h2>.*?</h2>)', html_content)
    
    result = []
    section_count = 0
    
    for i, section in enumerate(sections):
        result.append(section)
        
        # If this is an h2 header, increment section count
        if section.startswith('<h2>'):
            section_count += 1
            
            # Insert ad after 2nd and 4th major sections
            if section_count == 2 or section_count == 4:
                result.append(in_article_ad)
    
    # If we have a long article but few h2s, insert ads based on content length
    final_content = ''.join(result)
    
    # Count paragraphs to determine if we need more ads
    paragraph_count = len(re.findall(r'<p>', final_content))
    
    # For articles with many paragraphs but few sections, add ads differently
    if paragraph_count > 15 and section_count < 3:
        # Split by paragraphs and insert ads every 8-10 paragraphs
        paragraphs = re.split(r'(<p>.*?</p>)', final_content)
        final_result = []
        p_count = 0
        
        for part in paragraphs:
            final_result.append(part)
            if part.startswith('<p>'):
                p_count += 1
                if p_count % 8 == 0:  # Every 8th paragraph
                    final_result.append(in_article_ad)
        
        return ''.join(final_result)
    
    return final_content

def create_html_from_template(frontmatter, html_content):
    """Create full HTML page from template"""
    
    title = frontmatter.get('title', 'Blog Post')
    description = frontmatter.get('description', 'A blog post by Mahabub Alam Arafat')
    keywords = ', '.join(frontmatter.get('keywords', []))
    date = frontmatter.get('date', datetime.now().strftime('%Y-%m-%d'))
    read_time = frontmatter.get('readTime', '5 min read')
    category = frontmatter.get('category', 'Technology')
    slug = frontmatter.get('slug', 'blog-post')
    
    template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="author" content="Mahabub Alam Arafat">
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
    
    <!-- Open Graph Meta Tags -->
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://mahabubarafat.online/blog/{slug}.html">
    <meta property="og:site_name" content="Mahabub Alam Arafat - Portfolio">
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {{"@context": "https://schema.org","@type": "BlogPosting","headline": "{title}","description": "{description}","author": {{"@type": "Person","name": "Mahabub Alam Arafat"}},"datePublished": "{date}","dateModified": "{date}","publisher": {{"@type": "Person","name": "Mahabub Alam Arafat"}},"mainEntityOfPage": {{"@type": "WebPage","@id": "https://mahabubarafat.online/blog/{slug}.html"}},"keywords": {keywords_json}}}
    </script>
    
    <title>{title} | Mahabub Alam Arafat</title>
    <link rel="canonical" href="https://mahabubarafat.online/blog/{slug}.html">
    
    <!-- Google AdSense Code -->
    <meta name="google-adsense-account" content="ca-pub-6705222517983610">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6705222517983610"
            crossorigin="anonymous"></script>
    
    <link rel="stylesheet" href="blog_styling.css">
</head>
<body>
    <header>
        <h1>Mahabub Alam Arafat</h1>
        <p>Software Engineer - Blog</p>
    </header>

    <div class="container">
        <a href="../index.html#blog" class="back-link">← Back to Portfolio</a>
        
        <article>
            <header class="article-header">
                <h1 class="article-title">{title}</h1>
                <div class="article-meta">
                    <div class="meta-item">
                        <span>📅</span>
                        <time datetime="{date}">{formatted_date}</time>
                    </div>
                    <div class="meta-item">
                        <span>⏱️</span>
                        <span>{read_time}</span>
                    </div>
                    <div class="meta-item">
                        <span>🏷️</span>
                        <span>{category}</span>
                    </div>
                </div>
            </header>

            <div class="content">
                {html_content}
            </div>

            <!-- End of Article Ad -->
            <div class="ad-container" style="margin: 40px 0; text-align: center;">
                <ins class="adsbygoogle"
                     style="display:block; text-align:center;"
                     data-ad-layout="in-article"
                     data-ad-format="fluid"
                     data-ad-client="ca-pub-6705222517983610"
                     data-ad-slot="1879717900"></ins>
                <script>
                     (adsbygoogle = window.adsbygoogle || []).push({});
                </script>
            </div>

            <div class="social-share">
                <h3>Share this article</h3>
                <div class="share-buttons">
                    <a href="https://linkedin.com/shareArticle?mini=true&url=https://mahabubarafat.online/blog/{slug}.html&title={title}" target="_blank" class="share-btn share-linkedin">Share on LinkedIn</a>
                    <a href="https://twitter.com/intent/tweet?url=https://mahabubarafat.online/blog/{slug}.html&text={title}" target="_blank" class="share-btn share-twitter">Share on Twitter</a>
                </div>
            </div>

            <div class="author-bio">
                <h3>About the Author</h3>
                <p><strong>Mahabub Alam Arafat</strong> is a Software Engineer at ShareTrip with 2+ years of production experience. He specializes in backend development, API optimization, and turning legacy systems into modern, maintainable code.</p>
                <p><a href="../index.html#contact">Get in touch</a> | <a href="https://linkedin.com/in/mahabubarafat" target="_blank">LinkedIn</a> | <a href="https://github.com/MahabubArafat" target="_blank">GitHub</a></p>
            </div>
        </article>
    </div>

    <footer>
        <p>© 2025 Mahabub Alam Arafat. All rights reserved.</p>
    </footer>
</body>
</html>'''
    
    # Use string replace instead of format to avoid issues with curly braces in content
    html = template
    html = html.replace('{title}', title)
    html = html.replace('{description}', description)
    html = html.replace('{keywords}', keywords)
    html = html.replace('{date}', date)
    html = html.replace('{read_time}', read_time)
    html = html.replace('{category}', category)
    html = html.replace('{slug}', slug)
    html = html.replace('{html_content}', html_content)
    html = html.replace('{formatted_date}', datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y'))
    html = html.replace('{keywords_json}', json.dumps(frontmatter.get('keywords', [])))
    
    return html

def build_blog_post(markdown_file):
    """Build a single blog post from markdown"""
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, markdown_content = parse_frontmatter(content)
        html_content = markdown_to_html(markdown_content)
        full_html = create_html_from_template(frontmatter, html_content)
        
        # Generate output filename
        slug = frontmatter.get('slug', Path(markdown_file).stem)
        output_file = f"blog/{slug}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ Built: {markdown_file} -> {output_file}")
        return {
            'slug': slug,
            'title': frontmatter.get('title', 'Blog Post'),
            'description': frontmatter.get('description', ''),
            'date': frontmatter.get('date', ''),
            'readTime': frontmatter.get('readTime', '5 min read'),
            'category': frontmatter.get('category', 'Technology'),
            'file': output_file
        }
        
    except Exception as e:
        print(f"❌ Error building {markdown_file}: {e}")
        return None

def main():
    """Main build function"""
    print("🚀 Building blog posts...")
    
    markdown_dir = Path("blog/markdown")
    if not markdown_dir.exists():
        print("❌ No blog/markdown directory found")
        return
    
    built_posts = []
    
    # Build all markdown files
    for md_file in markdown_dir.glob("*.md"):
        if md_file.name not in ['template.md', 'README.md', 'ADSENSE_SETUP.md']:  # Skip template and docs
            post_info = build_blog_post(md_file)
            if post_info:
                built_posts.append(post_info)
    
    if built_posts:
        print(f"✅ Successfully built {len(built_posts)} blog post(s)")
        print("📝 Remember to update your blog index and showcase!")
    else:
        print("ℹ️ No blog posts to build")

if __name__ == "__main__":
    main()
