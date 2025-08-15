# Markdown Blog System

This folder contains markdown files that get converted to HTML blog posts.

## How to Write a New Blog Post

1. **Create a new `.md` file** in this folder (e.g., `my-new-post.md`)

2. **Start with frontmatter** (the metadata at the top):
```yaml
---
title: "Your Awesome Blog Title"
description: "SEO description (150-160 characters max)"
keywords: ["keyword1", "keyword2", "keyword3"]
date: "2025-01-15"
readTime: "5 min read"
category: "Technology"
slug: "your-blog-slug"
---
```

3. **Write your content in markdown** below the frontmatter

4. **Build the HTML** by running:
   - Windows: Double-click `build-blog.bat`
   - Command line: `python build_blog.py`

5. **Update your portfolio** - The script will tell you to update the blog index and showcase

## Markdown Tips

- Use `# Title` for main headings
- Use `## Section` for sections
- Use `**bold**` and `*italic*` for emphasis
- Use \`code\` for inline code
- Use triple backticks for code blocks:
  ```javascript
  const example = "code block";
  ```
- Use `- item` for bullet lists
- Use `> Quote` for blockquotes

## File Structure

```
blog/
├── markdown/           # Your markdown files go here
│   ├── template.md     # Template to copy from
│   └── your-post.md    # Your actual posts
├── your-post.html      # Generated HTML (don't edit)
└── blog_styling.css    # Styles for all blogs
```

## Example Post Structure

```markdown
---
title: "How I Fixed That Bug"
description: "The story of debugging a mysterious issue in production"
keywords: ["debugging", "production", "bug fix"]
date: "2025-01-15"
readTime: "5 min read"
category: "Debugging"
slug: "how-i-fixed-that-bug"
---

# How I Fixed That Bug

**TL;DR:** It was a missing semicolon. Always is.

## The Problem

Everything was broken and I didn't know why...

## The Solution

After 3 cups of coffee and questioning my life choices...

## The Lesson

Always check the basics first.
```

That's it! Much easier than writing HTML by hand.
