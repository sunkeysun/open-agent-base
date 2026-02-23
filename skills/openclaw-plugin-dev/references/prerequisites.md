# 通道插件开发前置条件

在开始开发新通道插件之前，需要收集以下信息。本清单帮助你准备所有必要的资料，确保开发过程顺利进行。

## 快速检查清单

### ✅ 必需信息（必须提供）

| # | 信息项 | 说明 | 示例 |
|---|--------|------|------|
| 1 | 通道 ID | 唯一标识符，小写字母 | `dingtalk`, `feishu` |
| 2 | 通道名称 | 显示名称 | `钉钉`, `飞书` |
| 3 | 连接模式 | Webhook 或 WebSocket | `webhook` |
| 4 | 认证方式 | API 认证类型 | `App ID + Secret`, `Token` |
| 5 | 发送消息 API | 发送消息的端点和格式 | API 文档链接 |
| 6 | 接收消息格式 | Webhook/消息回调的数据结构 | JSON 示例 |

### 🔶 建议信息（提高开发效率）

| # | 信息项 | 说明 | 默认值 |
|---|--------|------|--------|
| 7 | 通道别名 | 其他常用名称 | `[channelId]` |
| 8 | 官方文档 | API 文档链接 | - |
| 9 | SDK 信息 | 是否有官方 SDK | 无 |
| 10 | 消息类型 | 支持的消息类型 | 仅文本 |
| 11 | 群聊支持 | 是否支持群聊 | 否 |
| 12 | 媒体支持 | 是否支持图片/文件 | 否 |

---

## 详细信息收集表

### 一、基本信息

```
通道 ID: ________________  (如: dingtalk, feishu, lark)
通道名称: ________________  (如: 钉钉, 飞书)
通道别名: ________________  (如: dt, fs - 用逗号分隔)
官方文档: ________________  (API 文档 URL)
```

### 二、连接模式

**选择一种：**

- [ ] **Webhook 模式** - 平台主动推送消息到你的服务器
  - 需要：公网服务器、HTTPS
  - 示例：企业微信、钉钉、Telegram

- [ ] **WebSocket 模式** - 建立长连接接收消息
  - 需要：官方 SDK 或 WebSocket API
  - 示例：飞书、Lark

### 三、认证信息

**需要哪些凭证？**（选择所有适用的）

- [ ] App ID / Client ID
- [ ] App Secret / Client Secret
- [ ] Token / Bot Token
- [ ] Encoding AES Key（加密密钥）
- [ ] 其他：________________

**凭证获取方式：**
```
描述如何获取这些凭证：
1. 访问 ________________
2. 创建应用...
3. 获取 ________________
```

### 四、发送消息 API

**API 端点：**
```
POST https://________________
```

**请求头：**
```json
{
  "Authorization": "Bearer <token>",
  "Content-Type": "application/json"
}
```

**请求体示例：**
```json
{
  "to": "<用户ID或群ID>",
  "msgType": "text",
  "content": "消息内容"
}
```

**成功响应示例：**
```json
{
  "errcode": 0,
  "msgid": "message_id_123"
}
```

### 五、接收消息格式

**Webhook 数据示例（Webhook 模式）：**
```json
{
  "msgId": "消息ID",
  "fromUserId": "发送者ID",
  "chatId": "会话ID",
  "chatType": "single/group",
  "msgType": "text/image/file",
  "content": "消息内容或JSON"
}
```

**或 WebSocket 事件示例（WebSocket 模式）：**
```json
{
  "event": "message.receive",
  "data": {
    "message": { ... }
  }
}
```

### 六、功能支持

| 功能 | 是否支持 | 备注 |
|------|----------|------|
| 私聊 | 是 / 否 | |
| 群聊 | 是 / 否 | |
| @提及 | 是 / 否 | 群聊是否需要 @ 才响应 |
| 图片发送 | 是 / 否 | |
| 图片接收 | 是 / 否 | |
| 文件发送 | 是 / 否 | |
| 文件接收 | 是 / 否 | |
| 消息更新 | 是 / 否 | |
| 消息删除 | 是 / 否 | |
| 流式响应 | 是 / 否 | |

### 七、签名验证（如适用）

**算法：**
- [ ] HMAC-SHA256
- [ ] AES 加密
- [ ] 其他：________________

**验证步骤：**
```
1. 获取请求头中的签名: ________________
2. 计算预期签名: ________________
3. 比较签名
```

### 八、SDK 信息（如适用）

**是否有官方 SDK？**
- [ ] 是 - SDK 名称：________________
  - npm 包：________________
  - 文档：________________
- [ ] 否 - 使用原生 HTTP API

### 九、特殊需求

```
描述任何特殊需求或限制：
- 消息长度限制：________________
- 速率限制：________________
- 加密要求：________________
- 其他：________________
```

---

## 信息收集完成后

将以上信息整理成以下格式，提供给 Claude：

```yaml
channel:
  id: dingtalk
  name: 钉钉
  aliases: [dt, ding]
  docs: https://open.dingtalk.com/document/

mode: webhook

auth:
  - appId
  - appSecret

send_api:
  endpoint: https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2
  headers:
    Authorization: Bearer <access_token>
  body_example: |
    {
      "agent_id": "xxx",
      "userid_list": "user123",
      "msg": {
        "msgtype": "text",
        "text": { "content": "消息内容" }
      }
    }

receive_format: |
  {
    "msgId": "xxx",
    "senderId": "user123",
    "conversationId": "xxx",
    "msgtype": "text",
    "text": { "content": "消息内容" }
  }

features:
  direct_message: true
  group_message: true
  mention_required: true
  send_image: true
  receive_image: true
  send_file: false
  receive_file: false

signature:
  algorithm: hmac-sha256
  header: signature

sdk: none
```

---

## 示例：钉钉插件信息收集

### 已收集信息

```yaml
channel:
  id: dingtalk
  name: 钉钉
  aliases: [dt, ding]
  docs: https://open.dingtalk.com/document/orgapp/the-robot-sends-a-group-message

mode: webhook

auth:
  - appKey (即 Client ID)
  - appSecret (即 Client Secret)

send_api:
  endpoint: https://api.dingtalk.com/v1.0/robot/oToMessages/batchSend
  method: POST
  headers:
    x-acs-dingtalk-access-token: <access_token>
  body_example: |
    {
      "robotCode": "dingxxx",
      "userIds": ["user123"],
      "msgKey": "sampleText",
      "msgParam": "{\"content\":\"消息内容\"}"
    }

receive_format: |
  {
    "headers": {
      "timestamp": "1234567890",
      "sign": "xxx"
    },
    "body": {
      "msgtype": "text",
      "text": { "content": "消息内容" },
      "msgId": "xxx",
      "createAt": 1234567890,
      "conversationType": "1=单聊,2=群聊",
      "conversationId": "xxx",
      "conversationTitle": "群名称",
      "senderId": "user123",
      "senderNick": "用户昵称",
      "senderCorpId": "corp123",
      "senderStaffId": "staff123",
      "chatbotUserId": "bot123",
      "atUsers": [
        { "dingtalkId": "xxx", "staffId": "staff123" }
      ]
    }
  }

features:
  direct_message: true
  group_message: true
  mention_required: true  # 群聊需要 @
  send_image: true
  receive_image: true
  send_file: true
  receive_file: true

signature:
  algorithm: hmac-sha256
  header: sign
  timestamp_header: timestamp
  secret_field: appSecret

sdk: none
```

---

## 快速开始模板

如果你想快速开始，只需提供以下最基本信息：

```
通道名称: 钉钉
官方文档: https://open.dingtalk.com/
连接模式: Webhook
```

Claude 会帮你补充其他必要信息的询问。
