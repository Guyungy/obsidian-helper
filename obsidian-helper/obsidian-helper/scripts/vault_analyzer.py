import os
import argparse
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
import re
from pathlib import Path
from collections import Counter

def parse_frontmatter(content):
    if not HAS_YAML:
        return {}
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except:
            return {}
    return {}

def scan_vault(vault_path):
    print(f"Scanning vault at: {vault_path}")
    stats = {
        "total_files": 0,
        "md_files": 0,
        "folders": 0,
        "tags": Counter(),
        "empty_files": [],
        "links": {},  # file -> list of links
        "backlinks": Counter() # file -> incoming count
    }
    
    for root, dirs, files in os.walk(vault_path):
        if ".obsidian" in root or ".git" in root or "assets" in root:
            continue
            
        stats["folders"] += 1
        for file in files:
            stats["total_files"] += 1
            if file.endswith(".md"):
                stats["md_files"] += 1
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, vault_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not content.strip():
                            stats["empty_files"].append(rel_path)
                        
                        frontmatter = parse_frontmatter(content)
                        if "tags" in frontmatter:
                            tags = frontmatter["tags"]
                            if isinstance(tags, list):
                                stats["tags"].update(tags)
                            elif isinstance(tags, str):
                                stats["tags"].update([t.strip() for t in tags.split(",")])
                        
                        # Inline tags
                        inline_tags = re.findall(r'#(\w+)', content)
                        stats["tags"].update(inline_tags)

                        # Extract wiki-links: [[LinkName]] 或 [[LinkName|Alias]]
                        links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
                        stats["links"][rel_path] = links
                        for link in links:
                            # Normalize link (remove extension if added, etc. - Obsidian usually doesn't add .md)
                            stats["backlinks"][link] += 1
                except Exception as e:
                    print(f"Error reading {file}: {e}")
                    
    return stats

def analyze_graph(stats):
    print("\n--- Graph Density Analysis ---")
    
    # Hubs: High outgoing OR high incoming
    hubs = []
    for file, out_links in stats["links"].items():
        score = len(out_links) + stats["backlinks"][Path(file).stem]
        hubs.append((file, score, len(out_links), stats["backlinks"][Path(file).stem]))
    
    hubs.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop Potential MOC Candidates (Hubs):")
    for file, score, out, inc in hubs[:5]:
        print(f"- {file} (Score: {score}, Out: {out}, In: {inc})")

    # Islands: No outgoing AND no incoming
    islands = []
    for file in stats["links"].keys():
        stem = Path(file).stem
        if not stats["links"][file] and stats["backlinks"][stem] == 0:
            islands.append(file)
            
    print(f"\nOrphaned Notes (Islands): {len(islands)}")
    for file in islands[:5]:
        print(f"- {file}")
    if len(islands) > 5:
        print("  ...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan", action="store_true")
    parser.add_argument("--graph", action="store_true")
    parser.add_argument("path", help="Path to the vault or folder")
    
    args = parser.parse_args()
    
    if args.scan or args.graph:
        stats = scan_vault(args.path)
        
        if args.scan:
            print("\n--- Vault Summary ---")
            print(f"Total Folders: {stats['folders']}")
            print(f"Total Files: {stats['total_files']}")
            print(f"Markdown Files: {stats['md_files']}")
            print(f"Top 5 Tags: {stats['tags'].most_common(5)}")
            if stats['empty_files']:
                print(f"Empty Files found: {len(stats['empty_files'])}")
        
        if args.graph:
            analyze_graph(stats)
