# 使用场景扩展 — SunkeyOS

## 生活 OS 全景覆盖

### 工作场景

| 用户说 | AI 行为 |
|--------|---------|
| "今天加班到11点，很累" | → 写入 work-logs，更新 daily，标记 #overtime #mood/tired |
| "今晚通宵赶项目" | → 写入 work-logs，标记 #allnighter，记录项目名 |
| "今天开了3个小时会议" | → 写入 daily 时间线，#work |
| "需求又改了，挺烦的" | → 写入 daily 随手记，#mood/stressed #work |
| "上线了！很顺利" | → 写入 daily，#work #mood/happy，可关联项目文件 |
| "今天被老板批了" | → 写入 daily 反思区，#work #mood/negative |

### 旅行场景

| 用户说 | AI 行为 |
|--------|---------|
| "国庆去杭州玩了3天" | → 创建 trips/杭州-202410.md，初始化行程框架 |
| "今天在西湖边吃了东坡肉，超好吃" | → Append 到对应 trip 文件的对应 Day |
| "飞机延误2小时，到酒店已经凌晨了" | → Append trip 文件，#travel #mood/tired |
| "这次旅行4/5分" | → 更新 trip 文件的总体评价 |

### 健康场景

| 用户说 | AI 行为 |
|--------|---------|
| "今天跑步5公里" | → 写入 Areas/health/exercise-log.md + daily |
| "今天睡了9小时" | → 更新 daily 的睡眠记录 |
| "最近总是肩膀疼" | → 写入 Areas/health/body-issues.md |
| "体重 70kg" | → 写入 Areas/health/weight-log.md（追加日期+体重） |

### 财务场景

| 用户说 | AI 行为 |
|--------|---------|
| "买了新手机，花了8000" | → 写入 Areas/finance/expenses.md |
| "这个月发工资了，XXX元" | → 写入 Areas/finance/income.md |
| "今天吃饭花了120" | → 写入 daily + finance/expenses.md |

### 学习场景

| 用户说 | AI 行为 |
|--------|---------|
| "webpack entry output loader plugin的关系是..." | → 写入 Resources/tech/webpack.md |
| "发现一篇好文章 [URL]" | → 写入 Resources/reading/TITLE.md，提取摘要 |
| "React hooks 的闭包陷阱" | → 写入 Resources/tech/react.md（Append） |
| "学了个新命令 git bisect" | → 写入 Resources/tech/git.md（Append） |

### 社交关系场景

| 用户说 | AI 行为 |
|--------|---------|
| "今天和朋友吃饭，聊了很多" | → 写入 daily，可选择是否记录人名到 Areas/relationships/ |
| "老同学结婚了" | → 写入 Areas/relationships/friends.md + daily |

---

## 检索与召回场景

### 时间类检索

| 用户问 | 检索路径 | 输出格式 |
|--------|----------|----------|
| 今年加了多少班 | Glob work-logs/2026-*.md，统计加班字段 | 汇总表 |
| 上周我干了什么 | 读取 daily/ 上周 5 个文件 | 时间线列表 |
| 3月份有没有通宵 | Grep #allnighter in work-logs/2026-03-*.md | 匹配列表 |
| 今年去了哪些地方 | Glob trips/*.md + 读取 frontmatter | 地点列表 |

### 技术类检索

| 用户问 | 检索路径 | 输出格式 |
|--------|----------|----------|
| webpack 怎么打包库 | Grep "webpack" in Resources/tech/ | 相关笔记 + 通用知识 |
| 我记过哪些 git 技巧 | 读取 Resources/tech/git.md | 笔记内容 |
| 关于 React 的笔记 | Grep "react" in Resources/ | 命中笔记列表 |

### 情绪/感受类检索

| 用户问 | 检索路径 | 输出格式 |
|--------|----------|----------|
| 今年有哪些开心的时刻 | Grep #mood/happy in daily/ | 时间线 |
| 我最近压力大吗 | 读取近期 daily 的 mood 字段 | 情绪趋势 |

---

## 主动关联规则

以下场景中，AI 应主动关联已有记忆，即使用户没有明说：

1. **用户讨论某技术话题** → 主动说"你在 Resources/tech/webpack.md 中记过相关内容"
2. **用户提到某个项目** → 关联 Projects/ 下的对应文件
3. **用户讨论旅行计划** → 主动提及"你之前去过XX，笔记在 trips/"
4. **用户问年度/月度回顾** → 主动读取 daily、work-logs、trips 后生成
5. **用户提到某人** → 可关联 Areas/relationships/ 中的相关记录

---

## 边界处理

| 情况 | 处理方式 |
|------|---------|
| 信息中无明确时间 | 使用当前日期，在备注中标注"时间推断" |
| 分类模糊 | 存入 Inbox，回复中给出建议分类 |
| 文件不存在 | 从模板创建，初始化 frontmatter |
| 信息涉及敏感内容 | 正常记录，不做内容审查 |
| 用户要修改已有记录 | 找到对应文件和位置，用 Edit 工具修改 |
| 批量信息 | 逐条处理，每条给出确认 |
