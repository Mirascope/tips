#!/usr/bin/env python3
"""
Prepare markdown posts for social media.
This script:
1. Processes markdown content
2. Verifies code blocks
3. Generates code images
4. Creates platform-specific versions
"""

import argparse
import os
import sys
import json
import re
import subprocess
from pathlib import Path
from typing import List, Dict

# Import functionality from our other scripts
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import our modules
from scripts.process_post import process_markdown_file, clean_for_social
from scripts.generate_images import process_code_blocks_from_file


def format_social_content(content: str) -> str:
    """
    Format content for social media platforms.
    Keep full content and preserve formatting including bullet points.
    """
    # Keep the content as is, preserving bullet points and other formatting
    return content


def create_twitter_thread(post_data: Dict, image_paths: Dict[str, List[str]]) -> List[str]:
    """
    Create a Twitter thread from the post data.
    Returns a list of tweet contents.
    
    First tweet: Hook/intro + problem statement + images
    Second tweet: Solution + takeaway + series branding
    """
    tweets = []
    
    # First tweet: Just hook and introduction (no title)
    first_tweet = ""
    
    # Get the hook text
    if "hook" in post_data and post_data["hook"]:
        first_tweet = f"**{post_data['hook']}**"
    
    # Add introduction text
    if "first_tweet" in post_data and post_data["first_tweet"]:
        # Extract content after the hook
        hook_pattern = f"\\*\\*{re.escape(post_data.get('hook', ''))}\\*\\*"
        intro_text = re.sub(r"^##.*?\n\n", "", post_data["first_tweet"]) # Remove title
        intro_text = re.sub(hook_pattern, "", intro_text).strip() # Remove hook
        
        if intro_text:
            if first_tweet:
                first_tweet += "\n\n" + intro_text
            else:
                first_tweet = intro_text

        
    tweets.append(first_tweet)
    
    # Second tweet: Solution + Takeaway
    second_tweet = ""
    
    # Add solution content
    solution = post_data.get("solution", "")
    if solution:
        solution = solution.replace("### The Solution: ", "**").replace("### The Solution ", "**")
        if not solution.startswith("**"):
            solution = "**Solution:** " + solution
        else:
            solution += "**"
        second_tweet = solution
    
    # Add takeaway content
    takeaway = post_data.get("takeaway", "")
    if takeaway:
        takeaway = takeaway.replace("### The Takeaway", "**Takeaway:**").strip()
        
        if second_tweet:
            second_tweet += "\n\n" + takeaway
        else:
            second_tweet = takeaway
    
    # Add series footer
    second_tweet += "\n\n#EffectiveAI #AIEngineering"
    
    tweets.append(second_tweet)
    
    return tweets


def prepare_social_post(markdown_file: str, output_dir: str, theme: str = "VSCode") -> Dict:
    """
    Prepare a markdown file for social media posting.
    Returns a dictionary with platform-specific content and image paths.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process markdown file
    print(f"Processing {markdown_file}...")
    post_data = process_markdown_file(markdown_file)
    
    # Generate code images
    images_dir = os.path.join(output_dir, "images")
    # print(f"Generating code images...")
    # image_paths = process_code_blocks_from_file(markdown_file, images_dir, theme)
    image_paths = {}
    
    # Format content for LinkedIn, removing title and starting with hook
    linkedin_content = post_data["clean_content"]
    
    # Remove the title line and start with the hook
    linkedin_content = re.sub(r"^##.*?\n\n", "", linkedin_content)
    
    # Create Twitter thread
    twitter_threads = create_twitter_thread(post_data, image_paths)
    
    # Prepare result
    result = {
        "title": post_data["title"],
        "verified": post_data["verified"],
        "image_paths": image_paths,
        "platforms": {
            "twitter": {
                "thread": twitter_threads,
                "thread_count": len(twitter_threads)
            },
            "linkedin": {
                "content": linkedin_content
            }
        }
    }
    
    # Write LinkedIn content
    with open(os.path.join(output_dir, "linkedin.txt"), "w") as f:
        f.write(linkedin_content)
    
    # Write Twitter thread
    for i, tweet in enumerate(twitter_threads):
        with open(os.path.join(output_dir, f"twitter_{i+1}.txt"), "w") as f:
            f.write(tweet)
    
    # Check if any images were actually generated
    if not os.path.exists(images_dir) or not any(os.path.exists(path) for path in image_paths):
        print("\nNOTE: Images may not have been generated. This could be because carbon-now-cli is not installed.")
        print("To install carbon-now-cli, run: npm install -g carbon-now-cli")
        print("The text content has been generated successfully, but you'll need to create images manually.")
        
        # Create the images directory anyway
        os.makedirs(images_dir, exist_ok=True)
        
        # We'll add placeholder information to the summary.json
        print("\nImage files will be moved from the root directory to the output directory.")
        print("Look for images with names like:")
        print(f"  - {os.path.basename(markdown_file).split('.')[0]}-*.png")
        
    # Move any images from root directory to the output directory
    base_filename = os.path.basename(markdown_file).split('.')[0]
    root_images = []
    
    # Look for carbon-now generated images with the base filename prefix
    for search_dir in [".", ".."]:
        # Carbon-now creates files with a random suffix pattern: tip001-AbCdEfGhIj.png
        try:
            results = subprocess.run(
                ["find", search_dir, "-maxdepth", "1", "-name", f"{base_filename}-*.png"],
                check=True, capture_output=True, text=True
            )
            found_images = [path for path in results.stdout.strip().split('\n') if path]
            root_images.extend(found_images)
        except subprocess.CalledProcessError:
            pass
        
        # Also check for our named patterns (from direct image generation)
        for pattern in [f"{base_filename}_BEFORE_*.png", f"{base_filename}_AFTER_*.png", f"{base_filename}_code_*.png"]:
            try:
                results = subprocess.run(
                    ["find", search_dir, "-maxdepth", "1", "-name", pattern],
                    check=True, capture_output=True, text=True
                )
                found_images = [path for path in results.stdout.strip().split('\n') if path]
                root_images.extend(found_images)
            except subprocess.CalledProcessError:
                pass
    
    # Move any found images to the output directory
    for img_path in root_images:
        if img_path and img_path not in ['.', '..']:
            try:
                img_name = os.path.basename(img_path)
                dest_path = os.path.join(images_dir, img_name)
                os.makedirs(images_dir, exist_ok=True)
                
                # Move the file
                print(f"Moving image {img_path} to {dest_path}")
                subprocess.run(["mv", img_path, dest_path], check=True)
                
                # Update the paths in our result
                for key in image_paths:
                    for i, path in enumerate(image_paths[key]):
                        if os.path.basename(path) == img_name:
                            image_paths[key][i] = dest_path
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"Error moving image {img_path}: {e}")
    
    # Write summary to JSON
    with open(os.path.join(output_dir, "summary.json"), "w") as f:
        # Create a copy of the result with relative paths for images
        json_result = result.copy()
        json_result["image_paths"] = [os.path.basename(p) for p in image_paths]
        json.dump(json_result, f, indent=2)
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Prepare markdown posts for social media.")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--output", help="Output directory for processed files")
    parser.add_argument("--theme", default="VSCode", help="Carbon theme to use")
    args = parser.parse_args()
    
    # If no output specified, create directory based on input filename
    if not args.output:
        base_name = os.path.basename(args.file).split(".")[0]
        args.output = f"output/{base_name}"
    
    # Process the markdown file
    result = prepare_social_post(args.file, args.output, args.theme)
    
    # Print summary
    print("\nPost preparation complete!")
    print(f"Title: {result['title']}")
    print(f"Code verified: {'Yes' if result['verified'] else 'No - review needed'}")
    print(f"Generated {len(result['image_paths'])} code images")
    print(f"Output saved to: {args.output}")
    
    # Print content info
    print(f"\nSocial media content:")
    
    # Twitter thread info
    print(f"\nTwitter thread (2 tweets):")
    for i, tweet in enumerate(result['platforms']['twitter']['thread']):
        if i == 0:
            print(f"- Tweet 1 (Hook + Intro): {len(tweet)} chars")
        else:
            print(f"- Tweet 2 (Solution + Takeaway): {len(tweet)} chars")
        print(f"  Saved to: {args.output}/twitter_{i+1}.txt")
    
    # LinkedIn info
    print(f"\nLinkedIn post:")
    print(f"- Length: {len(result['platforms']['linkedin']['content'])} chars")
    print(f"- Saved to: {args.output}/linkedin.txt")
    
    # Image info
    print(f"- Images: {len(result['image_paths'])}")


if __name__ == "__main__":
    main()