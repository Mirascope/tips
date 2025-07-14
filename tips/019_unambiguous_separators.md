---
tip_number: 19
tip_name: "Use Unambiguous Separators in Your Prompts"
categories: ["prompt-engineering", "security", "output-validation"]
x_link: "https://x.com/skylar_b_payne/status/1927424714349126010"
linkedin_link: "https://www.linkedin.com/posts/skylarbpayne_your-model-is-ignoring-or-mixing-up-instructions-activity-7333190617092530176-5cIA?utm_source=share&utm_medium=member_desktop&rcm=ACoAABKpCf4BI_Yx2u7h66sgi5z1NF3aEYFHgps"
---

## Effective AI Engineering #19: Use Unambiguous Separators in Your Prompts

**Is your model suddenly ignoring instructions or mixing up data?** Ambiguous separators let user content "leak" into your prompt structure, causing models to treat data as instructions and produce completely unexpected outputs.

When you need to clearly separate different sections of your prompt—like instructions from examples, or user input from context—choosing the wrong delimiters can create parsing ambiguity. Models may struggle to determine where one section ends and another begins, especially with nested content or special characters.

### The Problem

Many developers use markdown code fences or simple dashes for separation, which can become ambiguous when content itself contains similar patterns:

```python
# BEFORE: Ambiguous Markdown Separators
PROMPT_TEMPLATE = """
Please extract the code from this user message and explain it.

---
User message:
```python
def hello():
    print("world")
```
Please explain this code snippet.
---

Format your response as:
```
Explanation: [your explanation]
Code: [the extracted code]
```
"""

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template(PROMPT_TEMPLATE)
def extract_and_explain(user_message: str): ...
```

**Why this approach falls short:**

- **Parsing Confusion:** The model sees multiple `---` separators and nested ``` blocks, making it unclear which delimiters are structural vs. content
- **Content Conflicts:** When user input contains the same separators you use (markdown, code fences), the model may misinterpret boundaries
- **Inconsistent Results:** The ambiguity leads to unpredictable parsing, especially when content varies significantly

### The Solution: XML-Style Unambiguous Separators

A better approach is to use XML-like tags that are inherently unambiguous and rarely appear in user content. XML provides clear opening and closing boundaries that models understand well.

```python
# AFTER: Unambiguous XML Separators
PROMPT_TEMPLATE = """
Please extract the code from this user message and explain it.

<user_message>
{user_message}
</user_message>

<instructions>
Format your response as:
- Explanation: [your explanation]  
- Code: [the extracted code]
</instructions>
"""

@llm.call(provider='openai', model='gpt-4o-mini')
@prompt_template(PROMPT_TEMPLATE)
def extract_and_explain(user_message: str): ...
```

**Why this approach works better:**

- **Clear Boundaries:** XML tags have unambiguous start/end markers (`<tag>` and `</tag>`) that don't conflict with common content formats
- **Hierarchical Structure:** You can nest sections cleanly without confusion about which delimiter belongs where
- **Model-Friendly:** Most modern language models are trained extensively on XML/HTML and parse these structures reliably
- **Content-Agnostic:** User input can contain markdown, code, or other formats without breaking your prompt structure
- **Reduced Injection Risk:** Clear boundaries make it harder for malicious user input to "escape" its designated section and interfere with your instructions

### The Takeaway

Stop using ambiguous delimiters that can conflict with your content. XML-style tags provide unambiguous structure that models parse reliably, regardless of what users input. This approach reduces parsing errors and makes your prompts more robust across different content types. Remember to also consult your model provider's documentation—most have specific recommendations for prompt formatting that can further improve reliability.

---
*Part of the "Effective AI Engineering" series - practical tips for building better applications with AI components.*