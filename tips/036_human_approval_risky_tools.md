## Effective AI Engineering #36: Human Approval for Risky Tools

**3 AM. Slack notifications exploding. Your AI agent just wiped the entire user uploads folder.** You watch in horror as frantic messages pour in from customers who've lost years of files. What started as a simple "clean up duplicate files" request turned into a catastrophe because your AI agent couldn't tell the difference between actual duplicates and important variations.

The worst part? You realize this could have been prevented with a single approval step. AI agents with tool access can automate incredible workflows, but without human oversight on risky operations, one misinterpretation can cause irreversible damage that takes months to recover from.

### The Problem

Many developers give AI agents direct access to powerful tools without human oversight. This creates challenges that aren't immediately obvious:

```python
# BEFORE: Unrestricted file deletion
from mirascope.core import anthropic, prompt_template
import shutil

def delete_files(directory: str, pattern: str) -> str:
    """Delete files matching pattern - no safety checks"""
    deleted = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                deleted.append(file_path)
    return f"Deleted {len(deleted)} files: {deleted[:5]}..."

@anthropic.call("claude-3-5-sonnet-20241022", tools=[delete_files])
@prompt_template("Clean up duplicate files in the uploads directory: {request}")
def file_cleanup_agent(request: str): ...

# AI can immediately execute destructive operations
result = file_cleanup_agent("Remove all files with 'copy' in the name")
print(result)  # Could delete important files without warning
```

**Why this approach falls short:**

- **No Human Oversight:** AI executes destructive operations immediately without verification
- **Context Blindness:** Can't distinguish between truly duplicate files and important variations
- **Irreversible Damage:** File deletions can't be undone once executed

### The Solution: Human Approval with HumanLayer

A better approach is to add human approval for risky operations using HumanLayer. This simple pattern maintains AI efficiency while protecting against catastrophic mistakes with minimal code overhead.

```python
# AFTER: Human approval for risky file operations
from mirascope.core import anthropic, prompt_template
import os
import humanlayer as hl

@hl.require_approval()
def delete_files(directory: str, pattern: str) -> str:
    """Delete files matching pattern - now requires human approval"""
    deleted = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if pattern in file:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                deleted.append(file_path)
    return f"Deleted {len(deleted)} files: {deleted[:5]}..."

@anthropic.call("claude-3-5-sonnet-20241022", tools=[delete_files])
@prompt_template("Clean up duplicate files in the uploads directory: {request}")
def file_cleanup_agent(request: str): ...

# Now requires human approval before executing
result = file_cleanup_agent("Remove all files with 'copy' in the name")
# HumanLayer will:
# 1. Show the human operator what the AI wants to do
# 2. Wait for approval/denial  
# 3. Only execute if approved
print(result)
```

**Why this approach works better:**

- **Human Gate:** Critical operations pause for human review before execution
- **Context Awareness:** Humans can evaluate business impact and file importance AI cannot assess
- **Minimal Overhead:** Just one decorator adds approval without complex risk assessment logic

### The Takeaway

Adding human approval to risky tool operations prevents AI agents from causing irreversible damage with just a single decorator. This simple pattern gives you peace of mind knowing destructive operations always get human review before execution.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*