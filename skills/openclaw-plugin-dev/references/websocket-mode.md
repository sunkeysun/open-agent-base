# WebSocket 通道模式

本文档描述如何实现基于 WebSocket 的通道插件（如飞书/Lark）。

## 与 Webhook 模式的区别

| 特性 | Webhook 模式 | WebSocket 模式 |
|------|-------------|----------------|
| 连接方式 | HTTP 回调 | 长连接 |
| 服务器要求 | 需要公网 IP | 无需公网 IP |
| 消息延迟 | 低 | 低 |
| 实现复杂度 | 中等 | 较高 |
| 典型通道 | 企业微信、钉钉 | 飞书、Lark |

## 架构

```
┌─────────────────┐         ┌─────────────────┐
│   通道平台      │◄───────►│  WebSocket 连接 │
│  (Feishu/Lark)  │         │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │ EventDispatcher │
                            │  (消息分发器)    │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │ 消息处理器       │
                            │ handleIncoming  │
                            └────────┬────────┘
                                     │
                            ┌────────▼────────┐
                            │ OpenClaw Runtime│
                            └─────────────────┘
```

## 实现步骤

### 1. 安装 SDK

```bash
npm install @your-channel/sdk
```

### 2. 创建 WebSocket 提供者

```javascript
// receive.websocket.js
import * as SDK from "@your-channel/sdk";

export function startWebSocketProvider(options) {
  const { account, config, log, statusSink } = options;

  // 创建 SDK 客户端
  const client = new SDK.Client({
    appId: account.appId,
    appSecret: account.appSecret,
  });

  // 创建事件分发器
  const dispatcher = new SDK.EventDispatcher({}).register({
    "message.receive": async (data) => {
      await handleIncomingMessage(data, { client, account, config, log, statusSink });
    },
  });

  // 创建并启动 WebSocket 客户端
  const wsClient = new SDK.WSClient({
    appId: account.appId,
    appSecret: account.appSecret,
  });

  wsClient.start({ eventDispatcher: dispatcher });

  log.info("WebSocket client started");
  statusSink?.({ running: true, lastStartAt: Date.now() });

  return {
    stop: () => {
      log.info("Stopping WebSocket provider");
      // 清理连接
      statusSink?.({ running: false, lastStopAt: Date.now() });
    },
  };
}
```

### 3. 实现消息处理器

```javascript
async function handleIncomingMessage(data, ctx) {
  const { client, account, config, log, statusSink } = ctx;

  // 解析消息
  const message = data.message;
  if (!message) return;

  const messageId = message.id;
  if (isDuplicate(messageId)) return;

  const chatId = message.chat_id;
  const senderId = message.sender_id;
  const chatType = message.chat_type === "p2p" ? "single" : "group";
  const content = message.content;

  // 更新状态
  statusSink?.({ lastInboundAt: Date.now() });

  // 构建上下文
  const inboundCtx = {
    Body: content,
    From: senderId,
    To: chatId,
    ChatType: chatType,
    // ...
  };

  // 分发到 OpenClaw
  await dispatchToOpenClaw(inboundCtx, { client, chatId, log });
}
```

### 4. "正在思考"占位符

```javascript
let placeholderId = "";
let done = false;

const timer = setTimeout(async () => {
  if (done) return;
  try {
    // 发送占位符消息
    placeholderId = await sendMessage(client, chatId, "正在思考...");
  } catch {
    // 忽略失败
  }
}, 2500);

// 在 deliver 回调中
dispatcherOptions: {
  deliver: async (payload) => {
    done = true;
    clearTimeout(timer);

    const replyText = payload.text || payload;

    if (placeholderId) {
      // 更新占位符消息
      await updateMessage(client, placeholderId, replyText);
      placeholderId = "";
    } else {
      // 发送新消息
      await sendMessage(client, chatId, replyText);
    }
  },
}
```

### 5. 在 Gateway 中启动

```javascript
// channel.js
gateway: {
  startAccount: async (ctx) => {
    const account = ctx.account;

    ctx.log?.info(`Starting WebSocket provider for ${account.accountId}`);

    const provider = startWebSocketProvider({
      account,
      config: ctx.cfg,
      log: {
        info: (msg) => ctx.log?.info(msg),
        error: (msg) => ctx.log?.error(msg),
      },
      abortSignal: ctx.abortSignal,
      statusSink: (patch) => ctx.setStatus({ accountId: account.accountId, ...patch }),
    });

    return provider;
  },
}
```

## 消息更新/删除

WebSocket 模式的通道通常支持消息更新和删除：

```javascript
// 更新消息
async function updateMessage(client, messageId, text) {
  await client.im.message.update({
    path: { message_id: messageId },
    data: {
      msg_type: "text",
      content: JSON.stringify({ text }),
    },
  });
}

// 删除消息
async function deleteMessage(client, messageId) {
  try {
    await client.im.message.delete({ path: { message_id: messageId } });
  } catch {
    // 最佳努力清理
  }
}
```

## 状态管理

```javascript
// status adapter
status: {
  defaultRuntime: {
    accountId: DEFAULT_ACCOUNT_ID,
    running: false,
    lastStartAt: null,
    lastStopAt: null,
    lastError: null,
    lastInboundAt: null,
    lastOutboundAt: null,
  },

  buildChannelSummary: ({ snapshot }) => ({
    configured: snapshot.configured ?? false,
    running: snapshot.running ?? false,
    mode: "websocket",
    lastStartAt: snapshot.lastStartAt ?? null,
    lastStopAt: snapshot.lastStopAt ?? null,
    lastError: snapshot.lastError ?? null,
    lastInboundAt: snapshot.lastInboundAt ?? null,
    lastOutboundAt: snapshot.lastOutboundAt ?? null,
  }),
}
```

## 错误处理

```javascript
// WebSocket 重连
wsClient.on("error", (err) => {
  log.error(`WebSocket error: ${err.message}`);
  statusSink?.({ lastError: err.message });
});

wsClient.on("close", () => {
  log.warn("WebSocket connection closed");
  statusSink?.({ running: false });
  // SDK 通常会自动重连
});
```

## 测试

```javascript
// 模拟 WebSocket 消息
import { __internal } from "./receive.websocket.js";

it("should handle incoming message", async () => {
  const mockData = {
    message: {
      id: "msg_123",
      chat_id: "chat_456",
      sender_id: "user_789",
      chat_type: "p2p",
      content: "Hello",
    },
  };

  await __internal.handleIncomingMessage(mockData, mockContext);

  // 验证消息被正确处理
});
```

## 完整示例

参见飞书插件实现：[openclaw-feishu](https://github.com/AlexAnys/openclaw-feishu)

关键文件：
- `src/receive.ts` - WebSocket 消息处理
- `src/send.ts` - 消息发送
- `src/channel.ts` - ChannelPlugin 定义
