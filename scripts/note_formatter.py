import os
import re
import argparse
from datetime import datetime

def format_note(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract or Create YAML Frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if frontmatter_match:
        yaml_content = frontmatter_match.group(1)
        body = content[frontmatter_match.end():].strip()
    else:
        yaml_content = ""
        body = content.strip()

    title = os.path.splitext(os.path.basename(file_path))[0]
    date_str = datetime.now().strftime('%Y-%m-%d')

    # Simple YAML enrichment
    if 'title:' not in yaml_content:
        yaml_content += f'\ntitle: "{title}"'
    if 'created:' not in yaml_content:
        yaml_content += f'\ncreated: {date_str}'
    if 'updated:' not in yaml_content:
        yaml_content += f'\nupdated: {date_str}'
    
    # Determine type based on prefix
    if title.startswith('MOC-'): note_type = 'moc'
    elif title.startswith('Ref-'): note_type = 'ref'
    elif title.startswith('Atom-'): note_type = 'atom'
    elif title.startswith('Log-'): note_type = 'log'
    elif title.startswith('Sum-'): note_type = 'sum'
    else: note_type = 'atom'
    
    if 'type:' not in yaml_content:
        yaml_content += f'\ntype: {note_type}'
    if 'status:' not in yaml_content:
        yaml_content += '\nstatus: seedling'

    # 2. Inject AI Summary Block (if missing)
    if '> [!ABSTRACT]' not in body:
        # Simple heuristic for summary: first paragraph (skipping other callouts/headers)
        lines = body.split('\n')
        first_para = ""
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('>'):
                first_para = stripped
                break
        
        summary_block = f"> [!ABSTRACT] 核心概览\n> {first_para if first_para else '暂无摘要'}\n\n"
        body = summary_block + body

    # 3. Clean up formatting
    # Ensure H1 title is not repeated if frontmatter has it
    body = re.sub(f'^# {re.escape(title)}\n+', '', body, flags=re.MULTILINE)
    
    # Normalize list markers
    body = re.sub(r'^\s*[\*\+]\s+', '- ', body, flags=re.MULTILINE)

    # Reconstruct Note
    new_content = f"---\n{yaml_content.strip()}\n---\n\n{body}"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Formatted: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Obsidian Note Formatter")
    parser.add_argument("path", help="Path to a markdown file or directory")
    args = parser.parse_args()
    
    if os.path.isfile(args.path):
        format_note(args.path)
    elif os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            for file in files:
                if file.endswith('.md'):
                    format_note(os.path.join(root, file))
