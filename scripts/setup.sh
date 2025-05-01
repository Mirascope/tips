#!/bin/bash
# Setup script for the Social Media Post Automation

# Install Python dependencies using uv
echo "Installing Python dependencies..."
uv add requests

# Install carbon-now-cli for code image generation
echo "Installing carbon-now-cli..."
npm install -g carbon-now-cli

echo "Setup complete!"
echo "You can now use the scripts to prepare your social media posts."
echo "Example: uv run scripts/prepare_social_post.py tips/001_bulkhead.md --output output/tip001"