# Obsidian 笔记内容标准 (v1.0)

为了确保知识库的长期可读性与自动化可处理性，本标准定义了笔记的“理想结构”。

## 1. 元数据 (YAML Frontmatter)
每篇笔记必须包含以下 YAML 区块：
```yaml
---
title: "笔记标题 (与文件名一致)"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: atom | moc | ref | log | proj
tags: [主题1, 主题2]
status: seedling | budding | evergreen  # 笔记成熟度
---
```

## 2. 核心结构
笔记正文应遵循以下布局：

### 第一部分：核心摘要 (AI Summary)
使用 Obsidian 的 Callout 语法：
```markdown
> [!ABSTRACT] 核心概览
> 用一句话或几个要点描述本笔记的核心价值，方便在悬停预览时快速获取信息。
```

### 第二部分：关系上下文 (Context)
用于建立 MOC 连接或定义上下级关系：
- **Up**: [[父级MOC或主题]]
- **Related**: [[相关笔记A]], [[相关笔记B]]

---

### 第三部分：正文内容 (Main Content)
- 标题层级从 `##` 开始（`#` 仅用于 YAML 后的标题或由 Obsidian 预览生成）。
- 保持短段落，多用列表。

### 第四部分：参考与来源 (References)
- 仅适用于 `Ref-` 类笔记。
- 标明原始 URL 或书籍来源。

## 3. 格式化规范
- **列表与缩进**：统一使用 `-`。
- **链接**：优先使用 `[[双链]]`，避免使用 Markdown 标准链接（除非是外部链接）。
- **附件**：图片必须存放在指定的 `Assets` 文件夹，并采用 `![[image.png]]` 引用。

---

## 4. 不同类型的前缀规范回顾
- `MOC-`: 地图笔记（结构化链接）
- `Atom-`: 原子笔记（单一知识点）
- `Ref-`: 外部参考资料
- `Log-`: 实战日志/日记
- `Sum-`: 总结/方法论
