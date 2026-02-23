---
name: openclaw-plugin-dev
description: |
  OpenClaw 通道插件开发工具包。适用于：
  1. 为 OpenClaw 创建新的消息通道插件
  2. 用户要求开发/集成新的聊天平台（钉钉、飞书、Lark 等）
  3. 用户需要帮助了解 OpenClaw 插件架构或测试
  4. 将现有通道集成转换为 OpenClaw 插件

  支持 Webhook 和 WebSocket 两种模式，生成完整的、可测试的插件模板。
  启动后会检查前置条件，引导用户提供必要的通道信息。
---

# OpenClaw 通道插件开发

本技能帮助你创建 OpenClaw 消息通道插件。

## ⚠️ 重要：开发前准备

在开始之前，**必须**先收集通道的 API 信息。详见 [prerequisites.md](references/prerequisites.md)。

### 快速检查

开始前请确认你已准备好：

| # | 必需信息 | 你有吗？ |
|---|----------|----------|
| 1 | 通道名称（如"钉钉"） | ？ |
| 2 | 连接模式（Webhook/WebSocket） | ？ |
| 3 | 认证凭证（App ID/Secret/Token） | ？ |
| 4 | 发送消息 API 端点和格式 | ？ |
| 5 | 接收消息的数据格式（JSON 示例） | ？ |

**如果缺少以上信息，请先查阅通道的官方 API 文档。**

---

## 开发流程

### 第一步：信息收集

**如果用户只提供了通道名称，按以下顺序询问：**

```
我将帮你开发 [通道名称] 插件。请提供以下信息：

## 必需信息

1. **连接模式**：该通道使用 Webhook 还是 WebSocket？
   - Webhook：平台推送消息到你的服务器（需要公网 IP）
   - WebSocket：建立长连接接收消息（无需公网 IP）

2. **认证方式**：需要哪些凭证？
   - [ ] App ID + App Secret
   - [ ] Token（API Token / Bot Token）
   - [ ] Encoding AES Key
   - [ ] 其他

3. **发送消息 API**：
   - API 端点 URL
   - 请求格式（JSON 示例）

4. **接收消息格式**：
   - Webhook 收到的 JSON 格式
   - 或 WebSocket 事件格式

## 可选信息

5. **功能支持**：
   - 是否支持群聊？群聊是否需要 @ 提及？
   - 是否支持发送/接收图片？

6. **官方文档链接**：方便查阅 API 详情

请提供以上信息，或提供官方 API 文档链接，我会帮你整理。
```

### 第二步：生成模板

收集到必要信息后，生成插件：

```bash
python scripts/create_plugin.py \
  --channel-id <id> \
  --channel-label "<名称>" \
  --mode <webhook|websocket>
```

### 第三步：填充实现

根据收集的信息，填充以下 TODO：

| 文件 | TODO 内容 | 依据 |
|------|-----------|------|
| `channel.js` | `outbound.sendText` | 发送消息 API |
| `channel.js` | `configSchema` | 认证凭证 |
| `webhook.js` / `receive.websocket.js` | `parseMessage` | 接收消息格式 |

### 第四步：测试验证

```bash
npm test
```

### 第五步：集成部署

```bash
openclaw plugins install ./openclaw-plugin-<id>
```

---

## 连接模式选择

| 模式 | 适用通道 | 特点 |
|------|----------|------|
| **Webhook** | 企业微信、钉钉、Telegram | 需要公网服务器，HTTP 回调 |
| **WebSocket** | 飞书、Lark | 无需公网 IP，长连接 |

---

## 必须实现的部分

### 1. 出站适配器（channel.js）

```javascript
outbound: {
  sendText: async ({ cfg, to, text, accountId }) => {
    // 依据：发送消息 API
    // TODO: 调用通道 API 发送消息
    const userId = to.replace(/^mychannel:/, "");
    const account = resolveAccount(cfg, accountId);

    const response = await fetch("https://api.example.com/send", {
      method: "POST",
      headers: { "Authorization": `Bearer ${account.token}` },
      body: JSON.stringify({ to: userId, text }),
    });

    const data = await response.json();
    return { channel: "mychannel", messageId: data.id };
  },
}
```

### 2. 消息解析（webhook.js / receive.websocket.js）

```javascript
// 依据：接收消息格式
async function parseMessage(data, target) {
  return {
    fromUser: data.sender.id,      // 发送者 ID
    content: data.content.text,    // 消息内容
    chatType: "single" | "group",  // 聊天类型
    chatId: data.chat.id,          // 群聊 ID（如适用）
    msgType: "text",               // 消息类型
  };
}
```

### 3. 配置 Schema（channel.js）

```javascript
// 依据：认证凭证
configSchema: {
  schema: {
    properties: {
      appId: { type: "string", description: "App ID" },
      appSecret: { type: "string", description: "App Secret" },
    },
  },
  uiHints: {
    appSecret: { sensitive: true },
  },
}
```

---

## 信息收集模板

将收集到的信息整理成此格式，便于填充模板：

```yaml
channel:
  id: <通道ID>
  name: <显示名称>
  mode: webhook | websocket

auth:
  - appId
  - appSecret

send_api:
  endpoint: https://api.example.com/send
  method: POST
  headers:
    Authorization: Bearer <token>
  body:
    to: <用户ID>
    msgType: text
    content: <消息内容>

receive_format:
  msgId: <消息ID>
  senderId: <发送者ID>
  chatId: <会话ID>
  chatType: single | group
  msgType: text | image | file
  content: <消息内容>

features:
  group_chat: true/false
  mention_required: true/false
  send_image: true/false
  receive_image: true/false
```

---

## 测试

```bash
npm test
```

Mock 运行时支持独立测试，无需 OpenClaw 环境。

---

## 集成到 OpenClaw

```bash
# 安装插件
openclaw plugins install /path/to/plugin

# 配置 ~/.openclaw/openclaw.json
{
  "channels": {
    "mychannel": {
      "enabled": true,
      "appId": "...",
      "appSecret": "..."
    }
  }
}

# 重启
openclaw gateway run --force
```

---

## 参考文件

- **[prerequisites.md](references/prerequisites.md)** - 前置条件详细清单（必读）
- [channel-adapters.md](references/channel-adapters.md) - 适配器模式和示例
- [websocket-mode.md](references/websocket-mode.md) - WebSocket 模式指南
- [testing.md](references/testing.md) - 测试指南
