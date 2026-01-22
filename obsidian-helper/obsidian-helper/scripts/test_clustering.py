import os

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

test_files = [
    "Project-12月第一周待拍摄.md",
    "Project-SOP.md",
    "Project-工作规划.md",
    "Project-品牌规划.md",
    "Project-24年1月 第一周 待拍摄.json"
]

for f in test_files:
    print(f"{f} -> {identify_project_group(f)}")
