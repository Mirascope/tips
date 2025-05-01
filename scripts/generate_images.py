#!/usr/bin/env python3
"""
Generate code images for social media posts using carbon-now-cli.
Requires carbon-now-cli to be installed: npm install -g carbon-now-cli
"""

import argparse
import os
import subprocess
import sys
import tempfile
import json


def generate_image_with_carbon(
    code: str, 
    language: str, 
    output_path: str,
    theme: str = "VSCode",
) -> bool:
    """
    Generate a code image using carbon-now-cli.
    Returns True if successful, False otherwise.
    
    Parameters:
    - code: The code to render
    - language: The programming language
    - output_path: Where to save the image (ignored - carbon decides the output path)
    - theme: Carbon theme to use (ignored - using default settings)
    """
    # Create a temporary file with the code
    with tempfile.NamedTemporaryFile(suffix=f'.{language}', mode='w+', delete=False) as temp:
        temp_path = temp.name
        temp.write(code)
    
    # Run carbon-now on the temporary file
    # Note: carbon-now will automatically choose an output filename and location
    print("Running carbon-now to generate image...")
    name = os.path.basename(output_path).split('.')[0]
    subprocess.run(
        [
            "carbon-now", temp_path,
            "--save-to", os.path.dirname(output_path),
            "--save-as", name,
            "--settings", json.dumps({"titleBar": name, "language": language, "theme": theme})
        ],
        check=True,
        timeout=30 
    )


def process_code_blocks_from_file(
    markdown_file: str, 
    output_dir: str,
    theme: str = "VSCode"
) -> list[str]:
    """
    Extract code blocks from a markdown file and generate images.
    Returns a list of generated image paths.
    """
    # Get labeled code blocks from process_post.py
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from scripts.process_post import extract_code_blocks
    
    with open(markdown_file, 'r') as f:
        content = f.read()
    
    blocks = extract_code_blocks(content)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    image_paths = []
    base_filename = os.path.basename(markdown_file).split('.')[0]
    
    for i, (lang, code, label) in enumerate(blocks):
        if not lang:
            lang = "txt"  # Default to txt if no language specified
            
        # Skip non-code blocks or blocks with unrecognized languages
        if lang.lower() not in ["python", "javascript", "typescript", "java", "bash", "sh", "txt", "sql"]:
            continue
        
        # Create appropriate filename based on label
        if label == "BEFORE":
            output_filename = f"{base_filename}_BEFORE.png"
        elif label == "AFTER":
            output_filename = f"{base_filename}_AFTER.png"
        else:
            output_filename = f"{base_filename}_code.png"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
            
        output_path = os.path.join(output_dir, output_filename)
        
        # Generate the image with appropriate theme
        print(f"Generating image for {label if label else 'code'} block {i+1} ({lang})...")
        generate_image_with_carbon(
            code, lang, output_path, theme=theme
        )
        image_paths.append(output_path)

    return image_paths


def main():
    parser = argparse.ArgumentParser(description="Generate code images for social media posts.")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--output", default="images", help="Output directory for images")
    parser.add_argument("--theme", default="VSCode", help="Carbon theme to use")
    args = parser.parse_args()
    
    # Check if carbon-now-cli is installed
    try:
        subprocess.run(["carbon-now", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: carbon-now-cli is not installed or not in PATH.")
        print("Install it with: npm install -g carbon-now-cli")
        return
    
    # Process code blocks and generate images
    process_code_blocks_from_file(args.file, args.output, args.theme)


if __name__ == "__main__":
    main()