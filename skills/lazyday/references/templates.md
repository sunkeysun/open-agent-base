# 模板定义

## daily-note.md — 每日日记

```markdown
---
title: {{date}} 日记
date: {{date}}
day_type: {{work|rest|travel|sick}}
mood: {{1-5}}
location: {{地点}}
weather: {{天气}}
energy_level: {{1-5}}
tags: []
summary: {{一句话总结}}
created: {{date}}
modified: {{date}}
type: daily
---

## 今日要点

- {{placeholder}}

## 时间线

| 时间 | 事项 | 标签 |
|------|------|------|
| HH:MM | 事件描述 | #tag |

## 加班记录

{{#if has_overtime}}
- start: HH:MM
- end: HH:MM
- duration: X小时
- reason: {{原因}}
{{/if}}

## 饮食记录

- 早餐: {{内容}}
- 午餐: {{内容}}
- 晚餐: {{内容}}
- 零食: {{内容}}

## 运动与健康

- 运动: {{类型}} {{时长/里程}}
- 睡眠: {{时长}}小时
- 身体状态: {{描述}}

## 反思

- **开心的事:**
- **需要改进的:**
- **明日计划:**

## 随手记

> {{内容}}
```

## work-log.md — 加班记录

```markdown
---
title: {{date}} 加班记录
date: {{date}}
type: work-log
category: overtime
start_time: "{{HH:MM}}"
end_time: "{{HH:MM}}"
duration: {{数字}}
duration_hours: {{数字}}
location: {{地点}}
reason: {{加班原因}}
mood: {{1-5}}
is_allnighter: {{true|false}}
project: {{项目名}}
tags: [#work #overtime]
created: {{date}}
modified: {{date}}
related: []
---

## 加班详情

- **时间**: start_time - end_time (duration小时)
- **地点**: location
- **原因**: reason
- **心情**: mood/5
- **项目**: project

## 工作内容

1. {{具体工作}}

## 状态

- 身体状态: {{描述}}
- 能量水平: energy/5
- 心情: {{描述}}

## 本月统计（手动维护）

- monthly_count: {{数字}}
- monthly_hours: {{数字}}
```

## trip.md — 出行记录

```markdown
---
title: {{目的地}} 之旅
type: trip
destination: {{目的地}}
start_date: {{YYYY-MM-DD}}
end_date: {{YYYY-MM-DD}}
duration_days: {{数字}}
companions: [{{同行人}}]
transport: [{{交通方式}}]
rating: {{1-5}}
tags: [#travel]
created: {{date}}
modified: {{date}}
related: []
---

## 旅行概览

- **目的地**: destination
- **时间**: start_date ~ end_date (duration_days天)
- **同行人**: companions
- **交通**: transport
- **住宿**: {{酒店名/方式}}
- **总花费**: {{金额}}

---

## 行程记录

### Day X — {{日期}}

- **地点**: {{地点}}
- **活动**: {{做了什么事}}
- **饮食亮点**: {{特色美食}}
- **心情**: mood/5
- **花费**: {{金额}}
- **随笔**: {{感想}}

---

## 总体评价

- **最难忘的瞬间**: {{内容}}
- **最推荐的地方**: {{内容}}
- **踩坑提示**: {{内容}}
- **下次会改变**: {{内容}}
- **总体评分**: rating/5

## 照片记录

> {{相册链接或照片描述}}
```

## milestone.md — 重要时刻

```markdown
---
title: {{事件名}}
date: {{YYYY-MM-DD}}
type: milestone
category: {{life-event|achievement|gift|decision|other}}
importance: {{high|medium|low}}
tags: [#milestone]
created: {{date}}
modified: {{date}}
related: []
---

## 事件概述

- **时间**: date
- **地点**: {{地点}}
- **参与人**: {{人物}}
- **类型**: category

## 事件详情

{{详细描述}}

## 影响与意义

{{这件事的影响}}

## 关联记忆

- 相关日记: [[4. Records/daily/YYYY-MM-DD]]
- 相关项目: [[1. Projects/...]]
- 相关人物: {{人名}}

## 后续跟进

- [ ] {{待办事项}}
```

## habit-entry.md — 习惯追踪

```markdown
---
title: {{习惯名}} - {{日期}}
date: {{YYYY-MM-DD}}
type: habit
habit_name: {{习惯名}}
habit_type: {{exercise|reading|meditation|skill|other}}
status: {{completed|partial|missed}}
duration: {{时长}}
quantity: {{数量}}
note: {{备注}}
tags: [#habit #习惯名]
created: {{date}}
modified: {{date}}
related: []
---

## {{日期}} 打卡

- **习惯**: habit_name
- **类型**: habit_type
- **状态**: status
{{#if duration}}
- **时长**: duration
{{/if}}
{{#if quantity}}
- **数量**: quantity
{{/if}}

## 记录

{{记录内容}}

## 连续打卡

- 当前连续: {{X}} 天
- 最长连续: {{Y}} 天
```

## atomic-note.md — 原子笔记 (技术知识)

```markdown
---
title: {{主题}}
type: note
category: tech
tags: [{{技术标签}}]
created: {{date}}
modified: {{date}}
source: {{来源}}
source_url: {{URL}}
related: []
summary: {{一句话总结}}
---

## 概述

{{主题概述}}

## 关键要点

1. {{要点1}}
2. {{要点2}}
3. {{要点3}}

## 详细内容

{{详细笔记内容}}

## 代码示例

```{{语言}}
{{代码}}
```

## 相关资源

- [[相关笔记1]]
- [外部链接](URL)

## 实践应用

{{如何在实际项目中使用}}
```

## quick-capture.md — 快速捕获 (Inbox)

```markdown
---
title: {{自动生成或用户输入}}
created: {{ISO8601}}
modified: {{ISO8601}}
type: capture
source: {{input|chat|link|photo}}
tags: []
summary: ""
captured: {{date}}
---

## 原始信息

> {{原文}}

## AI 分析结果

| 要素 | 内容 |
|------|------|
| when | {{时间}} |
| where | {{地点}} |
| who | {{人物}} |
| what | {{事实}} |
| how | {{感受}} |

## 分类建议

- **建议分类**: {{PARA位置}}
- **建议标签**: {{#tag1 #tag2}}
- **建议存放位置**: {{完整路径}}

## 关联笔记

- [[相关笔记]]

## 后续行动

- [ ] 确认分类
- [ ] 补充信息
- [ ] 归档到正式位置
