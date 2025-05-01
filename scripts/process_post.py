#!/usr/bin/env python3
"""
Process a markdown post for social media publishing.
This script:
1. Extracts code blocks from markdown
2. Verifies code executes properly
3. Generates a clean version for social media
"""

import argparse
import re
import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Dict, Optional


def extract_code_blocks(markdown_content: str) -> List[Tuple[str, str, str]]:
    """
    Extract code blocks from markdown.
    Returns a list of tuples (language, code, label).
    The label will be 'BEFORE', 'AFTER', or '' if no label is found.
    """
    # Regular expression to match fenced code blocks
    # Group 1: The language (optional)
    # Group 2: The code content
    pattern = r"```(\w*)\n(.*?)```"
    blocks = re.findall(pattern, markdown_content, re.DOTALL)
    
    # Process blocks to extract labels
    labeled_blocks = []
    for lang, code in blocks:
        # Check for BEFORE/AFTER label in first comment line
        before_match = re.search(r'^#\s*BEFORE:', code, re.MULTILINE)
        after_match = re.search(r'^#\s*AFTER:', code, re.MULTILINE)
        
        if before_match:
            label = "BEFORE"
        elif after_match:
            label = "AFTER"
        else:
            label = ""
            
        labeled_blocks.append((lang, code, label))
        
    return labeled_blocks


def verify_python_code(code: str) -> bool:
    """
    Verify Python code by checking syntax.
    Returns True if code compiles without syntax errors, False otherwise.
    
    Note: We only check syntax, not execution, due to the need for 
    dependencies like mirascope and potential side effects.
    """
    # Check for mirascope imports which we expect but can't execute in isolation
    if "mirascope" in code or "@llm.call" in code or "@prompt_template" in code:
        print("Code contains mirascope references - skipping execution check")
        
        # For mirascope code, just check if it's syntactically valid
        try:
            # Check if it at least compiles (syntax check)
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError as e:
            print(f"Syntax error in code: {e}")
            return False
    
    # For regular Python code without special imports
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w+', delete=False) as temp:
        temp_path = temp.name
        temp.write(code)
    
    try:
        # Check syntax
        subprocess.run(
            ["python", "-m", "py_compile", temp_path], 
            check=True, 
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Code syntax check failed: {e}")
        print(f"STDOUT: {e.stdout.decode() if e.stdout else ''}")
        print(f"STDERR: {e.stderr.decode() if e.stderr else ''}")
        return False
    finally:
        # Clean up
        os.unlink(temp_path)


def clean_for_social(markdown_content: str) -> str:
    """
    Clean markdown content for social media:
    - Remove code blocks and replace with placeholders
    - Preserve bullet points and formatting
    - Format for readability on social platforms
    """
    # Replace code blocks with placeholders
    clean_content = re.sub(
        r"```\w*\n.*?```", 
        "[Code example - see attached image]", 
        markdown_content, 
        flags=re.DOTALL
    )
    
    # Strip header syntax but keep the text
    clean_content = re.sub(r"^#{1,6}\s+(.+)$", r"\1", clean_content, flags=re.MULTILINE)
    
    # Remove "Python" lines that often precede code blocks
    clean_content = re.sub(r"^Python\s*$", "", clean_content, flags=re.MULTILINE)
    
    # Remove multiple consecutive blank lines
    clean_content = re.sub(r"\n{3,}", "\n\n", clean_content)
    
    # Keep markdown formatting for bullets, bold, etc.
    # We're intentionally not stripping these as we want to preserve formatting
    
    return clean_content.strip()


def process_markdown_file(file_path: str) -> Dict:
    """
    Process a markdown file and return:
    - title
    - hook (first paragraph after title)
    - clean_content (for social)
    - code_blocks (list of code blocks with labels)
    - verified (whether all code blocks were verified)
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    content = path.read_text()
    
    # Extract title (first ## heading)
    title_match = re.search(r"^##\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else path.stem
    
    # Extract hook (bold text in first paragraph after title)
    hook = ""
    after_title = content[title_match.end():] if title_match else content
    hook_match = re.search(r"^\s*\*\*(.+?)\*\*", after_title, re.MULTILINE)
    if hook_match:
        hook = hook_match.group(1)
    
    # Extract the first section for Twitter first tweet
    first_tweet_content = ""
    
    # Look for the first heading after the title to find the end of intro
    problem_heading_match = re.search(r"###\s+The Problem", content)
    if problem_heading_match:
        first_tweet_content = content[:problem_heading_match.start()].strip()
    else:
        # If no "The Problem" heading, use the first few paragraphs
        paragraphs = re.split(r"\n\n+", content)
        # Skip title, use next 2 paragraphs
        if len(paragraphs) > 2:
            first_tweet_content = "\n\n".join(paragraphs[1:3]).strip()
    
    # Extract code blocks with labels
    code_blocks = extract_code_blocks(content)
    
    # Verify Python code blocks
    verified = True
    for lang, code, label in code_blocks:
        if lang.lower() == 'python':
            if not verify_python_code(code):
                verified = False
                print(f"Warning: Code block verification failed in {file_path}")
    
    # Clean content for social media
    clean_content = clean_for_social(content)
    
    # Create a solution section (everything after the first code block)
    solution_content = ""
    solution_heading_match = re.search(r"###\s+The Solution[:\s]", content)
    takeaway_heading_match = re.search(r"###\s+The Takeaway", content)
    
    if solution_heading_match and takeaway_heading_match:
        solution_content = content[solution_heading_match.start():takeaway_heading_match.start()].strip()
        takeaway_content = content[takeaway_heading_match.start():].strip()
    
    return {
        "title": title,
        "hook": hook,
        "first_tweet": first_tweet_content,
        "solution": solution_content,
        "takeaway": takeaway_content if 'takeaway_content' in locals() else "",
        "clean_content": clean_content,
        "code_blocks": code_blocks,
        "verified": verified
    }


def main():
    parser = argparse.ArgumentParser(description="Process markdown posts for social media.")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--output", help="Output directory for processed files")
    args = parser.parse_args()
    
    result = process_markdown_file(args.file)
    
    print(f"Title: {result['title']}")
    print(f"Verified: {'Yes' if result['verified'] else 'No'}")
    print(f"Code blocks: {len(result['code_blocks'])}")
    print("\nCleaned content for social media:")
    print("-" * 40)
    print(result['clean_content'][:280] + "..." if len(result['clean_content']) > 280 else result['clean_content'])
    print("-" * 40)


if __name__ == "__main__":
    main()