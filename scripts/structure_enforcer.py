import os
import argparse
import shutil
import re
import yaml

def move_file(src, dest):
    """Safely move file and create directories if needed."""
    if os.path.abspath(src) == os.path.abspath(dest):
        return
    print(f"Moving: {src} -> {dest}")
    dest_dir = os.path.dirname(dest)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    try:
        shutil.move(src, dest)
    except Exception as e:
        print(f"Error moving {src}: {e}")

def trash_file(path, vault_root):
    """Safe delete: move file to Archive/Trash in the vault."""
    if not os.path.exists(path):
        print(f"Error: path does not exist: {path}")
        return
    
    rel_path = os.path.relpath(path, vault_root)
    trash_dir = os.path.join(vault_root, "Archive", "Trash")
    dest = os.path.join(trash_dir, rel_path)
    
    print(f"Trashing: {path} -> {dest}")
    dest_dir = os.path.dirname(dest)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    shutil.move(path, dest)

def rename_file(old_path, new_name):
    """Rename a file in its current directory."""
    dir_name = os.path.dirname(old_path)
    new_path = os.path.join(dir_name, new_name)
    if os.path.abspath(old_path) == os.path.abspath(new_path):
        return
    print(f"Renaming: {old_path} -> {new_path}")
    os.rename(old_path, new_path)

def get_note_type(file_path):
    """Determine note type (moc, log, project, ref, atom, sum) from content or prefix."""
    basename = os.path.basename(file_path)
    ext = os.path.splitext(file_path)[1].lower()
    
    # 1. Blocklist for system files
    system_files = ['workspace.json', 'app.json', 'community-plugins.json', 'core-plugins.json', 
                   'graph.json', 'appearance.json', 'hotkeys.json', 'command-palette.json',
                   'package.json', 'package-lock.json', '.DS_Store']
    if basename in system_files or basename.startswith('.'):
        return None

    # 2. Prioritize Keywords for Type Detection (fixes mis-prefixed files)
    log_keywords = ["会议", "周会", "Log", "日志", "复盘"]
    project_keywords = ["待拍摄", "计划", "任务", "Project", "SOP", "工作流", "规划"]
    moc_keywords = ["MOC", "目录", "Index", "Map", "指南"]
    
    if any(k.lower() in basename.lower() for k in log_keywords): return 'log'
    if any(k.lower() in basename.lower() for k in project_keywords): return 'project'
    if any(k.lower() in basename.lower() for k in moc_keywords): return 'moc'
    if basename.startswith('MOC-'): return 'moc'

    # 3. Try reading content for type
    if ext in ['.md', '.json']:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(2000)
                # Check YAML for .md
                if ext == '.md':
                    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        data = yaml.safe_load(match.group(1))
                        if data:
                            if 'type' in data: return data['type'].lower()
                            if 'status' in data and data['status'] == 'active': return 'project'
                # Check JSON for log-like indicators
                elif ext == '.json':
                    if any(k in content for k in ["周会", "会议", "Meeting", "Log"]): return 'log'
                    if '"block_type":' in content or '"text_run":' in content: return 'atom'
        except:
            pass
    
    # 4. Fallback to existing Prefix
    if basename.startswith('Log-'): return 'log'
    if basename.startswith('Project-'): return 'project'
    if basename.startswith('Ref-'): return 'ref'
    if basename.startswith('Sum-'): return 'sum'
    if basename.startswith('Atom-'): return 'atom'
    
    return None

# Global API Config
API_CONFIG = {
    "api_key": None,
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo"
}

# Type-to-Prefix Mapping
TYPE_PREFIX_MAP = {
    "moc": "MOC-",
    "log": "Log-",
    "project": "Project-",
    "ref": "Ref-",
    "sum": "Sum-",
    "atom": "Atom-",
    "default": "Atom-"
}

def auto_rename_file(file_path, ntype):
    """Ensure the file has the CORRECT prefix based on its type."""
    basename = os.path.basename(file_path)
    prefixes = list(TYPE_PREFIX_MAP.values())
    
    # Identify and strip existing prefix if it belongs to our set
    clean_name = basename
    for p in prefixes:
        if basename.startswith(p):
            clean_name = basename[len(p):]
            break
            
    prefix = TYPE_PREFIX_MAP.get(ntype, TYPE_PREFIX_MAP["default"])
    return prefix + clean_name

def get_semantic_category(file_path):
    """Ask AI to classify note into a Chinese Folder Name."""
    content = ""
    basename = os.path.basename(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(5000)
    except:
        return "待整理"

    # Weighted Keyword Scoring System (Simulated AI)
    # Weights: Filename match = 10 points, Content match = 1 point
    
    SCORES = {
        "人工智能": 0, "区块链": 0, "运动健康": 0, "技术储备": 0, 
        "营销运营": 0, "安全隐私": 0, "人文社交": 0, "生产效率": 0, 
        "阅读摘录": 0, "管理复盘": 0, "生活琐事": 0
    }
    
    # Extensive Keyword Dictionary (Internal Knowledge)
    KEYWORDS = {
        "人工智能": ["AI", "人工智能", "ChatGPT", "Claude", "LLM", "DeepSeek", "模型", "Prompt", "CompreFace", "训练", "算法", "机器人", "Midjourney", "Stable Diffusion", "GPT", "Transformer", "神经网络", "AIGC", "Copilot"],
        "区块链": ["区块链", "以太坊", "Ethereum", "Solidity", "Web3", "Crypto", "合约", "比特币", "BTC", "ETH", "DeFi", "Mining", "挖矿", "钱包", "公链", "交易所", "Token", "NFT", "DAO"],
        "运动健康": ["马拉松", "跑步", "健身", "运动", "减肥", "跑鞋", "全马", "半马", "健康", "肌肉", "有氧", "配速", "心率", "耐力", "力量", "饮食", "减脂", "瑜伽", "普拉提", "Meditation", "冥想"],
        "技术储备": ["Linux", "Ubuntu", "Docker", "Python", "编程", "服务器", "代码", "GitHub", "Git", "正则", "脚本", "插件", "C4D", "Pandoc", "API", "JSON", "CSS", "HTML", "Java", "Rust", "Golang", "SQL", "Database", "VNC", "NAS", "OpenWrt", "TTRSS", "WordPress", "宝塔", "穿透", "内网", "终端", "Shell", "Bash", "开发", "Debug"],
        "营销运营": ["小红书", "营销", "运营", "爆款", "流量", "文案", "种草", "广告", "投放", "账号", "脚本", "拍摄", "视频", "抖音", "剪映", "CapCut", "直播", "博主", "达人", "IP", "私域", "转化", "粉丝", "涨粉", "变现", "B2B", "SOP", "裂变", "用户", "增长"],
        "安全隐私": ["安全", "隐私", "OSINT", "渗透", "黑客", "漏洞", "加密", "解密", "溯源", "社工", "情报", "追踪", "代理", "VPN", "网络安全", "攻防", "木马", "病毒", "防护"],
        "人文社交": ["心理", "社交", "情感", "恋爱", "MBTI", "PUA", "亲密关系", "沟通", "情商", "人际", "社会", "哲学", "人性", "价值观", "思维", "情绪", "焦虑", "抑郁", "两性", "婚姻"],
        "生产效率": ["效率", "Obsidian", "Notion", "工作流", "知识管理", "PKM", "GTD", "方法论", "工具", "软件", "SOP", "模板", "看板", "清单", "笔记", "整理", "归档", "复盘", "时间管理"],
        "阅读摘录": ["阅读", "读书", "书评", "摘录", "文献", "Ref", "知乎", "文章", "观点", "引用", "资料", "学习", "教程", "指南", "手册", "课程", "学历", "证书"],
        "管理复盘": ["管理", "周会", "会议", "OKR", "KPI", "团队", "招聘", "面试", "简历", "薪资", "职场", "领导力", "创业", "战略", "复盘", "总结", "规划", "目标"],
        "生活琐事": ["生活", "房产", "买车", "装修", "家居", "美食", "旅行", "购物", "快递", "说明书", "百科", "常识", "技巧", "维修", "投诉", "账单", "缴费", "社保", "公积金"]
    }

    # 1. Calculate Scores
    basename_lower = basename.lower()
    content_lower = content.lower()

    for category, keywords in KEYWORDS.items():
        for kw in keywords:
            kw_lower = kw.lower()
            # Filename match (High Weight)
            if kw_lower in basename_lower:
                SCORES[category] += 10
            # Content match (Low Weight)
            elif kw_lower in content_lower:
                SCORES[category] += content_lower.count(kw_lower)

    # 2. Determine Best Fit
    # Find category with max score
    best_category = max(SCORES, key=SCORES.get)
    max_score = SCORES[best_category]

    # Threshold: Need at least a strong keyword match
    if max_score >= 5:
        return best_category

    # 3. Dynamic Tag Fallback (if no category matched well)
    # Try to find a hashtag in content
    tags = re.findall(r'#([\w\u4e00-\u9fa5]+)', content)
    if tags:
        # Use first valid tag as folder name
        return tags[0]

    return "待整理"

def identify_project_group(filename):
    """Group files into logical Project Bundles based on keywords."""
    name = filename.lower()
    
    # 1. Video Production Project (拍摄, 计划, Dates)
    # Groups: 11月第一周, 拍摄计划...
    if any(k in name for k in ["拍摄", "脚本", "视频", "素材"]):
        return "VideoProduction 视频生产"
    # Catch date-based shooting plans that might miss the word 'shooting' but are clearly content logs
    if any(k in name for k in ["待拍摄", "周", "月"]) and "sop" not in name:
        return "VideoProduction 视频生产"
        
    # 2. Operations SOP Library (SOPs)
    if "sop" in name or "流程" in name or "手册" in name:
        return "OperationSOP 运营SOP"
        
    # 3. Marketing Campaigns (营销, 私域)
    if any(k in name for k in ["营销", "活动", "私域", "运营", "增长", "content"]):
        return "MarketingCampaign 营销活动"
        
    # 4. Strategic Planning (规划, Brand)
    if any(k in name for k in ["规划", "计划", "复盘", "strategy", "okr", "目标", "品牌"]):
        return "StrategicPlanning 战略规划"

    # Fallback: Use the file name as a standalone project
    # Remove extension and Project- prefix
    base = os.path.splitext(filename)[0]
    for prefix in ["Project-", "project-"]:
        if base.startswith(prefix):
            return base[len(prefix):]
    return base

def get_destination_dir(vault_root, file_path, ntype, args):
    """Determine the correct ACES pillar and subfolder."""
    if ntype == 'moc':
        return os.path.join(vault_root, "Atlas 知识库", "Maps")
    elif ntype == 'log':
        return os.path.join(vault_root, "Calendar 时间轴")
    elif ntype == 'project':
        # Route projects to their Smart Project Bundle
        filename = os.path.basename(file_path)
        proj_folder = identify_project_group(filename)
        return os.path.join(vault_root, "Effort 执行力", "Ongoing 进行中", proj_folder)
    else:
        # Atomic notes: Route to Atlas (Knowledge) or Spaces (Area)
        category = get_semantic_category(file_path)
        
        # ACES Routing Logic
        # Spaces: Personal Areas of Responsibility
        if category in ["生活琐事", "人文社交", "管理复盘", "运动健康"]:
            return os.path.join(vault_root, "Spaces 我的生活", category)
        
        # Atlas: External Knowledge
        elif category != "待整理":
            return os.path.join(vault_root, "Atlas 知识库", category)
            
        # Fallback: Inbox
        return os.path.join(vault_root, "Inbox 收集箱")

def auto_classify(vault_root):
    """Orchestrate the organization of the entire vault into ACES."""
    print(f"Starting Intelligent ACES Classification: {vault_root}")
    
    # Pillar Migration Map (Old -> New)
    PILLAR_MIGRATION = {
        "Inbox": "Inbox 收集箱",
        "Atlas": "Atlas 知识库",
        "Calendar": "Calendar 时间轴",
        "Effort": "Effort 执行力",
        "Spaces": "Spaces 我的生活",
        "Archive": "Archive 归档"
    }
    
    # 0. Migrate Old Pillars if they exist
    for old, new in PILLAR_MIGRATION.items():
        old_path = os.path.join(vault_root, old)
        new_path = os.path.join(vault_root, new)
        if os.path.exists(old_path) and not os.path.exists(new_path):
            print(f"Migrating Pillar: {old} -> {new}")
            shutil.move(old_path, new_path)
    
    # 1. Initialize Pillars
    pillars = list(PILLAR_MIGRATION.values()) + ["Atlas 知识库/Assets", "Atlas 知识库/Maps", "Archive 归档/Trash", "Effort 执行力/Ongoing 进行中"]
    for p in pillars:
        os.makedirs(os.path.join(vault_root, p), exist_ok=True)
        
    # Ensure Subfolders Exist
    # Atlas: Knowledge
    atlas_cats = ["人工智能", "区块链", "技术储备", "营销运营", "安全隐私", "生产效率", "阅读摘录"]
    for name in atlas_cats:
        os.makedirs(os.path.join(vault_root, "Atlas 知识库", name), exist_ok=True)
        
    # Spaces: Areas
    spaces_cats = ["生活琐事", "人文社交", "管理复盘", "运动健康"]
    for name in spaces_cats:
        os.makedirs(os.path.join(vault_root, "Spaces 我的生活", name), exist_ok=True)

    approved_subs_atlas = ["Assets", "Maps"] + atlas_cats
    approved_subs_spaces = spaces_cats
    approved_subs_effort = ["Ongoing 进行中"]
    approved_project_bundles = ["VideoProduction 视频生产", "OperationSOP 运营SOP", "MarketingCampaign 营销活动", "StrategicPlanning 战略规划"]

    # 2. Main Processing Pass
    for root, dirs, files in os.walk(vault_root):
        if any(p in root for p in [".obsidian", ".git", "Archive 归档", "Trash"]):
            continue
            
        for file in files:
            path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            
            # Skip Dotfiles
            if file.startswith('.'): continue

            # Identify system junk
            system_exts = ['.js', '.css', '.html', '.map', '.sh', '.py']
            if ext in system_exts and "scripts" not in root:
                trash_file(path, vault_root)
                continue

            # Note-like files (MD and Note-JSONs)
            if ext in ['.md', '.json']:
                ntype = get_note_type(path)
                
                # If it's a JSON but NOT a note (no content), treat as asset or trash
                if ext == '.json' and ntype is None:
                    if file in ['workspace.json', 'app.json', 'community-plugins.json']:
                        continue
                    dest_dir = os.path.join(vault_root, "Atlas", "Assets")
                    move_file(path, os.path.join(dest_dir, file))
                    continue
                
                if ntype:
                    new_filename = auto_rename_file(path, ntype)
                    dest_dir = get_destination_dir(vault_root, path, ntype, args)
                    move_file(path, os.path.join(dest_dir, new_filename))
                else:
                    # Move unidentified but non-asset MDs via AI/Score
                    if ext == '.md':
                        category = get_semantic_category(path) # Returns Chinese Name
                        # Route based on Category -> Pillar
                        if category in ["生活琐事", "人文社交", "管理复盘", "运动健康"]:
                            dest_base = os.path.join(vault_root, "Spaces 我的生活", category)
                        elif category != "待整理":
                            dest_base = os.path.join(vault_root, "Atlas 知识库", category)
                        else:
                            dest_base = os.path.join(vault_root, "Inbox 收集箱")
                            
                        new_filename = auto_rename_file(path, 'atom')
                        move_file(path, os.path.join(dest_base, new_filename))

            # Pure Assets
            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx', '.xlsx', '.pages', '.csv', '.webp', '.mp4', '.avif', '.mov', '.zip', '.txt']:
                dest_dir = os.path.join(vault_root, "Atlas 知识库", "Assets")
                move_file(path, os.path.join(dest_dir, file))

    # 3. Cleanup Legacy Folders and Hidden Junk
    print("Performing post-classification cleanup...")
    for root, dirs, files in os.walk(vault_root, topdown=False):
        if any(x in root for x in [".obsidian", ".git", "Archive 归档"]): continue
        
        rel = os.path.relpath(root, vault_root)
        
        # Protect Root Pillars
        if rel in pillars: continue
        
        # Protect Atlas Subfolders
        parts = rel.split(os.sep)
        if parts[0] == "Atlas 知识库" and len(parts) == 2:
            if parts[1] in approved_subs_atlas or not os.listdir(root):
                 # Allow deletion if empty and not approved, otherwise protect
                 if parts[1] in approved_subs_atlas: continue
        
        # Protect Spaces Subfolders
        if parts[0] == "Spaces 我的生活" and len(parts) == 2:
             if parts[1] in approved_subs_spaces: continue
             
        if parts[0] == "Effort 执行力":
            if len(parts) == 2 and parts[1] in approved_subs_effort: continue
            # For Ongoing subfolders (Level 3):
            # 1. Allow approved bundles
            # 2. Allow non-empty folders (fallback for unrecognized projects)
            if len(parts) == 3 and parts[1] == "Ongoing 进行中":
                 if parts[2] in approved_project_bundles or os.listdir(root):
                      continue

        if not os.listdir(root):
            try:
                os.rmdir(root)
            except:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto-classify", action="store_true", help="Route files to ACE pillars")
    parser.add_argument("--vault", help="Vault root path")
    parser.add_argument("--trash", help="Move file to trash")
    
    # API Args
    parser.add_argument("--api-key", help="OpenAI API Key")
    parser.add_argument("--api-base", help="OpenAI API Base URL")
    parser.add_argument("--model", help="Model name (e.g. gpt-3.5-turbo)")
    
    args = parser.parse_args()
    
    # Set Global API Config
    if args.api_key: API_CONFIG["api_key"] = args.api_key
    if args.api_base: API_CONFIG["base_url"] = args.api_base
    if args.model: API_CONFIG["model"] = args.model
    
    if args.trash:
        if not args.vault:
            print("Error: --vault is required")
        else:
            trash_file(args.trash, args.vault)
            
    if args.auto_classify:
        if not args.vault:
            print("Error: --vault is required")
        else:
            auto_classify(args.vault)
