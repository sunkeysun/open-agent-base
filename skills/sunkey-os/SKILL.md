---
name: sunkey-os
description: >
  SunkeyOS 是 Sunkey 的个人第二大脑系统，基于 iCloud Obsidian 仓库实现全自动的信息捕获、分类存储、检索召回和智能分析。

  使用此 Skill 的场景：
  （1）用户提供任何原始信息（一句话、一个链接、一段描述、图片说明），需要自动分析提炼并存入对应 Obsidian 笔记文件
  （2）用户问"我上周做了什么"、"今年加了多少班"、"国庆去哪了"等需要检索已有记录的问题
  （3）用户问技术问题（如 webpack、React），需要先检索本地知识库再回答
  （4）用户需要生成周报、月报、年度总结、旅行回顾等聚合报告
  （5）用户在日常对话中提及时间、地点、感受、事件等信息，应自动判断是否需要记录
  （6）用户说"记一下"、"记录"、"帮我记"、"存一下"等关键词时立即触发
  （7）用户问"我记过哪些关于XX的内容"、"帮我找XX相关的笔记"等检索请求
---

# SunkeyOS — 个人第二大脑操作手册

## 仓库路径

```
VAULT=/Users/sunkeysun/Library/Mobile Documents/iCloud~md~obsidian/Documents/SunkeyOS
```

所有文件操作均基于此路径。

## 目录结构

```
VAULT/
├── 0. Inbox/          # 暂存 — 未处理的原始捕获
├── 1. Projects/       # 项目 — 有明确目标和截止日期
│   ├── work/
│   └── life/
├── 2. Areas/          # 领域 — 持续管理的责任范围
│   ├── career/
│   ├── finance/
│   ├── health/
│   └── relationships/
├── 3. Resources/      # 资源 — 知识、文章、技术笔记
│   ├── tech/
│   ├── reading/
│   └── interests/
├── 4. Records/        # 记录 — 时间线式的生活档案
│   ├── daily/         # 每日日记 YYYY-MM-DD.md
│   ├── work-logs/     # 工作/加班记录 YYYY-MM-DD.md
│   ├── habits/        # 习惯追踪
│   └── trips/         # 出行记录
├── 5. Archives/       # 归档 — 已完成/过期内容
└── _templates/        # 模板库（勿直接修改）
```

## 核心工作模式

### 模式 A：捕获（Capture）

用户提供原始信息 → 自动分析 → 选择存储位置 → 写入文件 → 返回确认

**触发词**：记一下、记录、帮我记、存一下、加班了、去了、今天…

**分析提取要素（5W1H）**：

| 要素 | 说明 | 提取示例 |
|------|------|----------|
| when | 时间 | 今天/昨天/具体日期/相对时间 |
| where | 地点 | 公司/城市/具体场所 |
| who | 人物 | 自己/同事/朋友/家人 |
| what | 事实 | 发生了什么、做了什么 |
| how | 感受/评价 | 情绪、评分、心情 |
| why | 原因/目的 | 为什么做/为什么发生 |

**分类决策规则**（按优先级）：

```
含有"加班/通宵/工作"           → 4. Records/work-logs/YYYY-MM-DD.md
含有"去了/旅行/出行/玩"         → 4. Records/trips/TRIP-NAME.md
含有"每日/今天/日记"            → 4. Records/daily/YYYY-MM-DD.md
含有技术知识/工具/代码方法       → 3. Resources/tech/TOPIC.md
含有书/文章/读书笔记             → 3. Resources/reading/TITLE.md
含有健康/运动/饮食               → 2. Areas/health/TOPIC.md
含有财务/收入/支出               → 2. Areas/finance/TOPIC.md
含有项目/需求/任务（有截止日期） → 1. Projects/work/ 或 life/
其他模糊信息                     → 0. Inbox/YYYY-MM-DD-TITLE.md
```

**日期推断规则**：
- "今天" → 当前系统日期
- "昨天" → 当前日期 -1
- "上周X" → 计算具体日期
- 无时间信息 → 使用当前日期

**文件写入规则**：
1. 文件已存在 → Append 到对应章节（不覆盖）
2. 文件不存在 → 从 `_templates/` 读取对应模板创建
3. 写入后在文件末尾或对应 section 追加内容
4. 同一天的同类信息合并到同一文件

**附加元数据**（自动添加，便于后续检索）：
```yaml
# 在 frontmatter 中自动维护
tags: [#work, #overtime, #tech ...]
captured_at: YYYY-MM-DD HH:mm
```

---

### 模式 B：检索（Find）

用户提问关于过去的信息 → 搜索对应目录 → 读取相关文件 → 整理输出

**触发词**：我上周/上个月/今年 + 做了/去了/加了/记过… 找一下/搜索/有没有关于…

**检索策略**：

```
时间类问题（加班、日程）→ grep 搜索 4. Records/ 目录
技术类问题              → 先搜索 3. Resources/tech/ + Glob 相关文件
旅行类问题              → 搜索 4. Records/trips/
习惯/健康类             → 搜索 2. Areas/health/ + 4. Records/daily/
综合日记类              → 搜索 4. Records/daily/ 时间范围内文件
```

**检索后输出格式**：
- 列出找到的相关文件
- 提取关键信息摘要
- 标注信息来源（文件路径:行号）
- 如有多条，按时间排序

---

### 模式 C：报告（Report）

用户需要汇总统计 → 读取所有相关文件 → 聚合分析 → 生成结构化报告

**常见报告类型**（见 references/report-templates.md）：
- 加班统计：统计 work-logs 中的加班天数、时长、通宵次数
- 旅行回顾：汇总 trips 中的目的地、时长、同行人
- 年度总结：综合 daily + work-logs + trips + health
- 技术复盘：汇总 Resources/tech 中的笔记主题
- 习惯追踪：分析 habits 中的打卡记录

---

### 模式 D：知识问答（Ask）

用户问技术/知识问题 → 先检索本地知识库 → 结合已有笔记 + 自身知识回答

流程：
1. Grep 搜索 `3. Resources/` 相关关键词
2. 读取命中的文件
3. 整合本地笔记内容 + 已有知识
4. 明确标注"来自你的笔记"vs"来自通用知识"

---

## 写入格式规范

### Daily Note（4. Records/daily/YYYY-MM-DD.md）

追加格式：
```markdown
## 时间线

| 时间 | 事项 | 标签 |
|------|------|------|
| HH:MM | [事项] | #tag |
```

### Work Log（4. Records/work-logs/YYYY-MM-DD.md）

追加格式：
```markdown
## 加班记录 - YYYY-MM-DD

- **时间**: HH:MM - HH:MM（X 小时）
- **地点**: [地点]
- **原因**: [原因]
- **心情**: [心情评分]/5
- **备注**: [备注]
```

### Trip（4. Records/trips/DESTINATION-YYYYMM.md）

追加格式：
```markdown
## Day N - YYYY-MM-DD

- **地点**: [具体地点]
- **活动**: [做了什么]
- **同行**: [人员]
- **心情**: [心情]
- **亮点**: [记忆点]
```

### Tech Resource（3. Resources/tech/TOPIC.md）

追加格式：
```markdown
## [知识点标题] — YYYY-MM-DD

**来源**: [URL/文章/实践]

**核心要点**:
- 要点1
- 要点2

**代码示例**:
```language
code
```

**关联**: [[相关笔记]]
```

---

## 标签系统

| 标签 | 含义 |
|------|------|
| #work | 工作相关 |
| #life | 生活相关 |
| #tech | 技术知识 |
| #overtime | 加班 |
| #allnighter | 通宵 |
| #travel | 出行 |
| #health | 健康 |
| #finance | 财务 |
| #mood/happy | 开心 |
| #mood/tired | 疲惫 |
| #mood/stressed | 压力 |
| #project | 项目 |
| #learning | 学习 |
| #social | 社交 |
| #family | 家庭 |

---

## 执行规范

1. **始终先检查文件是否存在**，存在则追加，不存在则从模板创建
2. **时间推断要明确**，无法确定时用当前日期并在备注中说明
3. **写入后给出简短确认**，格式：`✓ 已记录到 [相对路径] — [一句话摘要]`
4. **检索时读取实际文件内容**，不要凭记忆猜测
5. **跨文件关联**：写入时自动检查是否需要在 daily note 中同步引用
6. **不确定分类时**优先存入 `0. Inbox/`，并在回复中说明建议分类

## 扩展场景参考

详见 references/scenarios.md
