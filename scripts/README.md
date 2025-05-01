# Social Media Post Automation

Scripts for automating preparation of content for social media platforms.

## Setup

Install dependencies using `uv`:

```bash
uv add requests
```

For generating code images, you'll need `carbon-now-cli`:

```bash
npm install -g carbon-now-cli
```

## Scripts

### `prepare_social_post.py`

Main script that processes a markdown post and prepares it for social media.

Usage:
```bash
./prepare_social_post.py /path/to/post.md --output output/post-name --preset Yeti
```

This will:
1. Process the markdown file to extract code blocks and clean content
2. Verify any Python code blocks execute properly
3. Generate code images using carbon-now-cli
4. Create platform-specific versions for Twitter and LinkedIn
5. Output files to the specified directory

### `process_post.py`

Library for processing markdown files for social media.

### `generate_images.py`

Library for generating code images using carbon-now-cli.

## Workflow

1. Write your markdown post in the `tips/` directory
2. Run `./prepare_social_post.py tips/001_bulkhead.md` to prepare it for social media
3. Review the output in the generated directory
4. Upload to Hypefury or your preferred scheduling tool

## Future Enhancements

- API integration with Hypefury for direct scheduling
- Support for additional social platforms
- Thread splitting for Twitter