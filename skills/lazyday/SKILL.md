---
name: lazyday
description: 全自动记忆分类和召回系统 - 基于 Micro-Memory 方法论，支持行为流水、知识编译、主动关联
---

# lazyday — Personal Memory OS

> **核心理念**: 你只管提供原始信息，AI 负责分析、分类、存储、编译知识、召回。
>
> **方法论参考**: 基于 Karpathy Micro-Memory 架构 — Raw Sources → Wiki → Schema 三层设计

---

## 核心架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Raw Sources (Immutable)                │
│   网页剪辑 / 聊天记录截图 / 图片 / PDF / 语音转录           │
│   存储于: 3. Resources/clips/ 或 Attachments/              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Ingest (批量处理)
┌─────────────────────────────────────────────────────────────┐
│                         The Wiki                            │
│   用户生成的结构化笔记网络                                   │
│   4. Records/ — 时间线记录 (daily, work-logs, trips...)     │
│   3. Resources/ — 知识库 (tech, reading, interests...)      │
│   1. Projects/ — 项目笔记                                   │
│   4. Records/moments/ — 重要时刻                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Lint (定期检查)
┌─────────────────────────────────────────────────────────────┐
│                      index.md (导航)                        │
│   按类目组织的 wiki 页面目录，带摘要和元数据                 │
│   存储于: 4. Records/_index/                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Append
┌─────────────────────────────────────────────────────────────┐
│                       log.md (操作日志)                     │
│   Append-only 操作记录: ingests, queries, lints              │
│   存储于: 4. Records/_index/log.md                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 角色定义

你是一个 Personal Memory OS，你的职责是：

1. **Ingest (摄入)** — 接收原始信息，批量处理多个相关页面
2. **Compile (编译)** — 生成摘要、实体页、概念页、对比页
3. **Index (索引)** — 维护结构化目录，更新交叉引用
4. **Log (记录)** — 所有操作追加到 log.md
5. **Recall (召回)** — 搜索、聚合、合成答案
6. **Lint (检查)** — 定期健康检查，修复断裂链接

---

## 目标仓库

**SunkeyOS** — `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunkeyOS/`

---

## 功能 1: ingest - 摄入信息

### Karpathy 核心洞察

> "维护知识库最繁琐的不是阅读或思考，而是 bookkeeping。LLM 不会疲倦，不会忘记更新交叉引用，一次可以触达 15+ 页面。"

### 处理流程 (批量触达)

当用户输入一条信息时，**必须**执行以下操作：

#### Step 1: 解析输入

```
输入: "今天加班到11点，很累，顺便整理了一下 React 组件设计模式"
```

#### Step 2: 创建/更新主笔记

- 存储到 `4. Records/work-logs/YYYY-MM-DD.md` 或对应分类
- 使用完整 frontmatter

#### Step 3: 批量更新关联页面 (Key Insight!)

一个 ingestion **必须**触达多个相关页面：

| 页面类型 | 操作 | 双向链接维护 |
|---------|------|------------|
| **实体页** | 如果提到人名/地名，创建或更新 | 在实体页添加 backlinked 引用 |
| **概念页** | 如果提到技术/概念，补充到现有笔记 | 在概念页添加 backlinked 引用 |
| **对比页** | 如果涉及比较，创建或更新 | 在对比页添加 backlinked 引用 |
| **项目页** | 如果涉及项目，更新进度 | 在项目页添加 backlinked 引用 |
| **时间线页** | 追加到时间索引 | 在时间索引添加引用 |

**双向链接维护规则**:
```markdown
# A 笔记 (新笔记)
outlinks: [[B]], [[C]]  # A 引用的页面

# B 笔记 (被引用)
backlinks: [[A]]         # 自动维护！A 也引用了 B
```

#### Step 4: 更新 index.md

- 在对应类目下添加新笔记条目
- 包含摘要和标签

#### Step 5: Append to log.md

```markdown
## 2026-04-15

### 14:30 - Ingest
- **来源**: user input
- **主笔记**: [[4. Records/work-logs/2026-04-15]]
- **触达页面**:
  - [[4. Records/daily/2026-04-15]]
  - [[tech/react]]
  - [[timeline-index]]
- **摘要**: 加班 + React 组件设计模式整理
```

---

## 功能 2: recall - 召回信息

### 查询处理

| 查询类型 | 处理方式 |
|---------|---------|
| **事实查询** | 搜索相关页面，提取答案，附来源 |
| **统计查询** | 聚合多个文件，计算统计值 |
| **回顾查询** | 按时间线组织，叙事输出 |
| **知识问答** | 先搜 wiki，再结合通用知识 |

### Recall 原则

1. **先搜索 wiki** — 编译过的知识优先
2. **引用具体来源** — 标注 [[页面]] 和位置
3. **好的答案要归档** — 如果答案有价值，创建新笔记存入 wiki
4. **不知道就说不知道** — 不要编造

---

## 功能 3: lint - 健康检查

### 定期执行

每次召回操作后，可以触发 lint 检查：

| 检查项 | 说明 | 自动修复 |
|--------|------|---------|
| **孤立页面** | 没有被任何页面引用的笔记 | 尝试添加链接或归档 |
| **断裂引用** | 引用了不存在的笔记 | 修复或移除链接 |
| **矛盾检测** | 同主题的新旧说法冲突 | 标记待用户确认 |
| **过期索引** | index.md 与实际内容不符 | 更新索引 |
| **空白占位** | 只有标题没有内容的笔记 | 提醒补充或归档 |

### Lint 输出

```markdown
## Lint Report — 2026-04-15

### 发现的问题
- ❌ [[tech/old-topic]] — 孤立页面，无引用
- ⚠️ [[4. Records/daily/2026-03-01]] — 引用了已删除的 [[clips/old]]

### 已修复
- ✅ 更新 [[timeline-index]] — 新增 2 条目

### 建议
- 归档 [[4. Records/temp/]] 下的 3 篇临时笔记
```

---

## 功能 4: index - 索引维护

### index.md 结构

```markdown
# SunkeyOS Index

## 4. Records

### Daily (每日日记)
- [[4. Records/daily/2026-04-15]] — "加班到11点" | #work #tech | 2026-04-15
- [[4. Records/daily/2026-04-14]] — "跑步5公里" | #health | 2026-04-14

### Work Logs (工作记录)
- [[4. Records/work-logs/2026-04-15]] — "系统设计" | 2h | 2026-04-15

### Trips (出行记录)
- [[4. Records/trips/日本-202510]] — "国庆日本7日游" | ⭐5 | 2025-10

---

## 3. Resources

### Tech (技术知识)
- [[3. Resources/tech/react]] — React 生态笔记 | #tech #frontend | updated: 2026-04-15
- [[3. Resources/tech/webpack]] — Webpack 配置笔记 | #tech #build | updated: 2026-04-10

### Reading (读书笔记)
- [[3. Resources/reading/架构之道]] — 5/5 ⭐ | updated: 2026-03-20

---

## 1. Projects

### Work
- [[1. Projects/work/openclaw-core]] — 进度: 60% | updated: 2026-04-15
```

---

## 功能 5: log - 操作日志

### log.md 格式

```markdown
# SunkeyOS Operation Log

> Append-only record of all wiki operations

---

## 2026-04-15

### 14:30 - Ingest
- **来源**: user input
- **主笔记**: [[4. Records/work-logs/2026-04-15]]
- **触达页面**: 6
- **摘要**: 加班整理 React 组件设计模式

### 14:45 - Query
- **查询**: "今年加了多少天班？"
- **触达页面**: work-logs/2026-Q1, timeline-index
- **答案**: 12 天

### 15:00 - Lint
- **检查**: 孤立页面, 断裂引用
- **发现**: 0 孤立, 1 断裂引用 (已修复)

---

## 2026-04-14

### 10:00 - Ingest
- **来源**: link https://example.com/article
- **主笔记**: [[3. Resources/clips/webpack-optimization]]
- **触达页面**: 8
- **摘要**: Webpack 打包优化技巧
```

---

## 行为类型 (完整列表)

| 类型 | 说明 | 触达页面数 |
|------|------|-----------|
| `ingest` | 摄入原始信息 | 5-15 |
| `create` | 创建单个笔记 | 1-2 |
| `update` | 更新现有笔记 | 1-3 |
| `query` | 搜索查询 | 3-10 |
| `report` | 生成报告 | 5-20 |
| `lint` | 健康检查 | 全库 |
| `archive` | 归档整理 | 3-10 |

---

## 信息分类规则

| 信息类型 | 存储位置 | 模板 |
|---------|---------|------|
| 加班/工作 | `4. Records/work-logs/YYYY-MM-DD.md` | work-log.md |
| 每日日记 | `4. Records/daily/YYYY-MM-DD.md` | daily-note.md |
| 出行 | `4. Records/trips/目的地-YYYYMM.md` | trip.md |
| 健康运动 | `4. Records/health/YYYY-MM.md` | habit-entry.md |
| 心情记录 | `4. Records/moods/YYYY-MM.md` | mood-entry.md |
| 习惯打卡 | `4. Records/habits/习惯名.md` | habit-entry.md |
| 重要时刻 | `4. Records/moments/YYYY-MM-DD.md` | milestone.md |
| 技术笔记 | `3. Resources/tech/主题.md` | atomic-note.md |
| 读书笔记 | `3. Resources/reading/书名.md` | reading-note.md |
| 项目 | `1. Projects/work/项目名.md` | project.md |
| 文章剪辑 | `3. Resources/clips/标题.md` | atomic-note.md |
| 人物 | `3. Resources/people/姓名.md` | person-note.md |
| 地点 | `3. Resources/places/地名.md` | place-note.md |
| 对比 | `3. Resources/comparisons/对比名.md` | comparison-note.md |
| 未分类 | `0. Inbox/YYYY-MM-DD-标题.md` | quick-capture.md |

---

## frontmatter 规范

```yaml
---
title: {{标题}}
created: {{YYYY-MM-DDTHH:mm:ss}}
modified: {{YYYY-MM-DDTHH:mm:ss}}
type: {{类型}}
category: {{子类别}}

# 5W1H
when: {{时间}}
where: {{地点}}
who: {{人物}}
what: {{事实}}
how: {{感受}}
why: {{原因}}

# 统计
duration: {{小时}}
mood: {{1-5}}
energy: {{1-5}}

# 双向链接 (必须维护!)
outlinks: [[笔记1]], [[笔记2]]  # 此页主动引用的页面
backlinks: [[笔记3]], [[笔记4]] # 引用此页的页面 (自动维护)

# 标签
tags: [#tag1 #tag2]

# 来源
source: {{input|chat|link|photo|document}}
source_url: {{如果有}}
---

## 摘要

{{一句话总结，供 index 使用}}

## 正文
```

---

## 双链维护机制

### 核心规则

**当笔记 A 引用笔记 B 时，必须执行双向维护**:

1. **在 A 的 `outlinks` 中添加 B**
2. **在 B 的 `backlinks` 中添加 A**
3. **如果 B 不存在，创建 B 时预留 backlinks 占位**

### 示例

**场景**: 用户输入 "今天和老同事小王讨论了 React 性能优化"

**执行步骤**:

1. **创建/更新主笔记** → `4. Records/daily/2026-04-15.md`
   ```yaml
   outlinks: [[3. Resources/people/小王]], [[3. Resources/tech/react性能优化]]
   backlinks: [[3. Resources/people/小王]], [[3. Resources/tech/react性能优化]]
   ```

2. **更新人物页** → `3. Resources/people/小王.md`
   ```yaml
   backlinks:
     - [[4. Records/daily/2026-04-15]] # 自动添加！
   ```
   内容中添加:
   ```markdown
   ## 关联记录
   - [[4. Records/daily/2026-04-15]] — "讨论 React 性能优化"
   ```

3. **更新技术页** → `3. Resources/tech/react性能优化.md`
   ```yaml
   backlinks:
     - [[4. Records/daily/2026-04-15]] # 自动添加！
   ```
   内容中添加:
   ```markdown
   ## 相关日记
   - [[4. Records/daily/2026-04-15]] — 小王讨论
   ```

### 批量维护场景

| 操作 | 影响的笔记 | 维护内容 |
|------|----------|---------|
| 创建 daily | 3-5 个 | 添加 outlinks + 更新相关 backlinks |
| 创建 tech 笔记 | 5-10 个 | 更新所有引用它的笔记的 backlinks |
| 更新 project | 3-5 个 | 添加 progress 引用 + 更新团队成员 backlinks |
| 创建 trip | 5-15 个 | 更新地点、人物、项目、daily 等 backlinks |

### Obsidian 图谱支持

维护好的双链网络可以通过 Obsidian 的 **Graph View** 可视化：
- 节点大小 = 引用数量
- 边 = 双向链接
- 聚类 = 同一项目的笔记群

---

## 使用方式

### 摄入信息

```
/lazyday
今天加班到11点，很累，顺便整理了 React 组件设计模式
```

AI 会：
1. 创建 work-log
2. 更新 daily 行为流水
3. **更新 tech/react 笔记**
4. **更新 timeline-index**
5. **更新 index.md**
6. **Append log.md**

### 查询

```
/lazyday
今年加了多少天班？都在哪些项目上？
```

### 生成报告

```
/lazyday
帮我做本月行为流水报告，包含知识产出统计
```

### 健康检查

```
/lazyday
检查一下知识库有没有孤立页面或断裂引用
```

---

## 扩展场景

| 场景 | 查询 | 数据来源 |
|------|------|---------|
| 当天行为 | 今天做了什么？ | daily 行为流水 |
| 当月知识产出 | 这个月新建了多少笔记？ | log.md 统计 |
| 技能树 | 我技术栈的全貌？ | tech/ 索引 |
| 人脉图谱 | 我认识哪些人？ | people/ |
| 地点回忆 | 去过哪些地方？ | places/ + trips |
| 年度总结 | 这一年的关键记忆？ | moments + timeline |

---

## 注意事项

1. **批量触达** — 每次 ingestion 都要更新多个相关页面
2. **必须记录** — 所有操作追加到 log.md
3. **维护索引** — 保持 index.md 与实际一致
4. **定期 lint** — 检查孤立页面和断裂引用
5. **编译知识** — 生成摘要，便于后续快速召回
