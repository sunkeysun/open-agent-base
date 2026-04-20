# 5W1H 要素提取规则

## when (时间)

### 识别模式

| 输入 | 提取结果 |
|------|---------|
| 今天 | 当前日期 |
| 昨天 | 昨天日期 |
| 昨天上午 | 昨天 + time: 上午 |
| 上周一 | 上周一日期 |
| 10月1日 | 今年10月1日 或 指定年份 |
| 国庆 | 国庆假期 (10月1-7日) |
| 最近 | 最近7天 |
| 这周/这月/今年 | 当前周期 |

### 扩展字段

```yaml
when: "2026-03-24"
when_type: # date | period | range | relative
when_detail: # morning | afternoon | evening | night | 具体时间
```

## where (地点)

### 识别模式

| 输入 | 提取结果 |
|------|---------|
| 公司 | 公司 |
| 家/家里 | 家里 |
| 杭州/上海/北京 | 城市名 |
| 西湖/天安门 | 地标名 |
| 高铁/飞机/火车 | 交通工具 |
| 餐厅/咖啡馆/酒店 | 场所类型 |

### 扩展字段

```yaml
where: "杭州"
where_type: # city | landmark | office | home | transit | venue
where_detail: # 具体地址或场所名
```

## who (人物)

### 识别模式

| 输入 | 提取结果 |
|------|---------|
| 我/自己 | 用户本人 |
| 老婆/老公/女朋友 | 亲密关系 |
| 老板/领导/同事 | 职场关系 |
| 朋友名 | 人名 |
| 团队/大家 | 群体 |

### 扩展字段

```yaml
who: ["老婆", "同事A"]
who_relation: # family | colleague | friend | acquaintance
```

## what (事实)

### 识别模式

| 类型 | 关键词 | 提取为 |
|------|--------|--------|
| 工作 | 加班,开会,出差,面试 | 工作相关 |
| 旅行 | 旅游,度假,出差,回家 | 出行相关 |
| 学习 | 学了,看了,读了,研究了 | 学习相关 |
| 健康 | 跑步,健身,体检,病了 | 健康相关 |
| 财务 | 花了,买了,赚了,发了工资 | 财务相关 |
| 社交 | 见了,聚会,约会,婚礼 | 社交相关 |

## how (感受)

### 识别模式

| 输入 | 提取结果 |
|------|---------|
| 累/很累/累死了 | mood: 1 |
| 有点累/比较累 | mood: 2 |
| 一般/普通 | mood: 3 |
| 开心/高兴/不错 | mood: 4 |
| 很开心/超开心/太棒了 | mood: 5 |

### 能量等级

| 输入 | 提取结果 |
|------|---------|
| 完全没精力 | energy: 1 |
| 比较累 | energy: 2 |
| 正常 | energy: 3 |
| 精神不错 | energy: 4 |
| 精力充沛 | energy: 5 |

## why (原因)

### 识别模式

| 输入 | 提取结果 |
|------|---------|
| deadline/项目紧急 | deadline |
| 需求/功能开发 | feature |
| bug/问题修复 | bugfix |
| 学习/提升 | learning |
| 度假/休息 | vacation |

---

## 组合提取示例

### 输入: "今天去杭州出差见客户，晚上加班到10点，很累"

```yaml
when: "2026-03-24"
when_detail: "白天出差, 晚上加班"
where: "杭州"
where_type: "city"
what: "出差见客户, 晚上加班"
how: "累"
why: "工作项目"
mood: 2
duration: 10 # 加班时长
tags: [#work #出差 #杭州 #加班]
```

### 输入: "国庆去了日本玩7天，每天暴走，累但很开心"

```yaml
when: "2025-10-01 to 2025-10-07"
when_type: "period"
when_detail: "7天"
where: "日本"
where_type: "country"
what: "旅行"
how: "累但开心"
mood: 4
energy: 2
duration: 7
tags: [#travel #日本 #国庆 #暴走]
```

### 输入: "今天跑了5公里，感觉很棒"

```yaml
when: "2026-03-24"
when_detail: "早上或指定时间"
where: ""
where_type: "unknown"
what: "跑步5公里"
how: "很棒"
mood: 5
energy: 4
duration: 0.5 # 估计时长
tags: [#exercise #running #健康]
```
