#!/usr/bin/env python3
"""
Extract frontmatter from tip markdown files and generate CSV metadata.
"""

import csv
import os
from pathlib import Path
from typing import Dict, List, Any
import yaml
import argparse


def extract_frontmatter(file_path: Path) -> Dict[str, Any]:
    """Extract YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file starts with frontmatter
    if not content.startswith('---'):
        return {}
    
    # Split content to get frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}
    
    try:
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter or {}
    except yaml.YAMLError:
        return {}


def process_tips_directory(tips_dir: Path) -> List[Dict[str, Any]]:
    """Process all markdown files in tips directory and extract metadata."""
    tips = []
    
    for file_path in sorted(tips_dir.glob('*.md')):
        # Skip intro file
        if file_path.name == '000_intro.md':
            continue
            
        frontmatter = extract_frontmatter(file_path)
        
        if frontmatter:
            # Convert categories list to space-separated string for CSV
            categories_str = ' '.join(frontmatter.get('categories', []))
            
            tip_data = {
                'tip_number': frontmatter.get('tip_number', ''),
                'tip_name': frontmatter.get('tip_name', ''),
                'markdown_file': file_path.name,
                'categories': categories_str,
                'x_link': frontmatter.get('x_link', ''),
                'linkedin_link': frontmatter.get('linkedin_link', '')
            }
            tips.append(tip_data)
        else:
            print(f"Warning: No frontmatter found in {file_path.name}")
    
    return tips


def write_csv(tips: List[Dict[str, Any]], output_file: Path):
    """Write tips metadata to CSV file."""
    fieldnames = ['tip_number', 'tip_name', 'markdown_file', 'categories', 'x_link', 'linkedin_link']
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tips)


def main():
    parser = argparse.ArgumentParser(description='Extract frontmatter from tips and generate CSV')
    parser.add_argument('--tips-dir', type=Path, default=Path('tips'), 
                       help='Directory containing tip markdown files')
    parser.add_argument('--output', type=Path, default=Path('tips_metadata.csv'),
                       help='Output CSV file path')
    
    args = parser.parse_args()
    
    if not args.tips_dir.exists():
        print(f"Error: Tips directory {args.tips_dir} does not exist")
        return 1
    
    tips = process_tips_directory(args.tips_dir)
    
    if not tips:
        print("Warning: No tips with frontmatter found")
        return 1
    
    write_csv(tips, args.output)
    
    print(f"Successfully extracted metadata for {len(tips)} tips")
    print(f"CSV written to: {args.output}")
    
    return 0


if __name__ == '__main__':
    exit(main())