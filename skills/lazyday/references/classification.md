# 信息分类规则

## 快速分类决策树

```
输入内容
  │
  ├─ 包含 URL/链接？
  │   └─ 是 → 3. Resources/clips/ 或根据内容类型分类
  │
  ├─ 包含时间+地点+活动？
  │   └─ 是 → 旅行/出差 → 4. Records/trips/
  │
  ├─ 包含"加班"/"通宵"/工作内容？
  │   └─ 是 → 4. Records/work-logs/
  │
  ├─ 包含心情/感受/日常活动？
  │   └─ 是 → 4. Records/daily/
  │
  ├─ 包含技术/编程/框架？
  │   └─ 是 → 3. Resources/tech/
  │
  ├─ 包含书名/读书感想？
  │   └─ 是 → 3. Resources/reading/
  │
  ├─ 包含健康/运动/饮食？
  │   └─ 是 → 4. Records/health/
  │
  ├─ 包含金钱/消费/收入？
  │   └─ 是 → 4. Records/finances/
  │
  ├─ 包含项目名+目标+截止日期？
  │   └─ 是 → 1. Projects/work/ 或 1. Projects/life/
  │
  └─ 无法分类 → 0. Inbox/
```

## 分类优先级

1. **Records (记录)** > **Resources (资源)** > **Projects (项目)** > **Inbox (收集箱)**
2. 当信息同时满足多个类别时，按优先级选择
3. 优先选择时间线类存储（Records），便于后续统计

## 标签系统

### 常用标签

**时间相关**:
- #morning #afternoon #evening #night
- #weekday #weekend #holiday

**情感相关**:
- #happy #tired #stressed #relaxed #frustrated #excited

**活动相关**:
- #work #meeting #travel #exercise #reading #learning

**状态相关**:
- #important #urgent #follow-up #review

## 存储路径速查

| 关键词 | 存储位置 |
|--------|---------|
| 加班/通宵/996 | `4. Records/work-logs/` |
| 旅游/出差/度假 | `4. Records/trips/` |
| 生日/纪念日/节日 | `4. Records/moments/` |
| 跑步/健身/运动 | `4. Records/health/` |
| 工资/消费/理财 | `4. Records/finances/` |
| 心情/情绪/感受 | `4. Records/moods/` |
| 习惯/打卡/养成 | `4. Records/habits/` |
| React/Vue/Webpack/..."等技术 | `3. Resources/tech/` |
| 《书名》/读书 | `3. Resources/reading/` |
| 项目/需求/任务 | `1. Projects/` |
| 无法分类 | `0. Inbox/` |
