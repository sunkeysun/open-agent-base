# Channel Adapters Reference

This document provides patterns and examples for implementing channel adapters.

## Table of Contents

- [Config Adapter](#config-adapter)
- [Outbound Adapter](#outbound-adapter)
- [Gateway Adapter](#gateway-adapter)
- [Directory Adapter](#directory-adapter)
- [Status Adapter](#status-adapter)
- [Streaming Support](#streaming-support)
- [Common Patterns](#common-patterns)

---

## Config Adapter

The config adapter manages channel configuration and account resolution.

### Basic Implementation

```javascript
config: {
  listAccountIds: (cfg) => {
    const channel = cfg?.channels?.mychannel;
    if (!channel || !channel.enabled) return [];
    return ["default"];
  },

  resolveAccount: (cfg, accountId) => {
    const channel = cfg?.channels?.mychannel;
    if (!channel) return null;

    return {
      id: accountId || "default",
      accountId: accountId || "default",
      enabled: channel.enabled !== false,
      token: channel.token || "",
      secret: channel.secret || "",
      webhookPath: channel.webhookPath || "/webhooks/mychannel",
      config: channel,
    };
  },

  defaultAccountId: (cfg) => {
    const channel = cfg?.channels?.mychannel;
    if (!channel || !channel.enabled) return null;
    return "default";
  },

  setAccountEnabled: ({ cfg, accountId, enabled }) => {
    if (!cfg.channels) cfg.channels = {};
    if (!cfg.channels.mychannel) cfg.channels.mychannel = {};
    cfg.channels.mychannel.enabled = enabled;
    return cfg;
  },

  deleteAccount: ({ cfg, accountId }) => {
    if (cfg.channels?.mychannel) {
      delete cfg.channels.mychannel;
    }
    return cfg;
  },
}
```

### Multi-Account Support

```javascript
config: {
  listAccountIds: (cfg) => {
    const channel = cfg?.channels?.mychannel;
    if (!channel || !channel.enabled) return [];

    // If accounts object exists, return its keys
    if (channel.accounts) {
      return Object.keys(channel.accounts);
    }

    return ["default"];
  },

  resolveAccount: (cfg, accountId) => {
    const channel = cfg?.channels?.mychannel;
    if (!channel) return null;

    const id = accountId || "default";

    // Check accounts object first
    if (channel.accounts?.[id]) {
      const accountConfig = channel.accounts[id];
      return {
        id,
        accountId: id,
        enabled: accountConfig.enabled !== false,
        token: accountConfig.token || channel.token || "",
        config: { ...channel, ...accountConfig },
      };
    }

    // Fallback to default
    return {
      id,
      accountId: id,
      enabled: channel.enabled !== false,
      token: channel.token || "",
      config: channel,
    };
  },
}
```

---

## Outbound Adapter

The outbound adapter sends messages from OpenClaw to the channel.

### Basic Text Sending

```javascript
outbound: {
  sendText: async ({ cfg, to, text, accountId }) => {
    const userId = to.replace(/^mychannel:/, "");

    // Get account config
    const account = resolveAccount(cfg, accountId);

    // Call channel API
    const response = await fetch("https://api.example.com/messages", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${account.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to: userId,
        text: text,
      }),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return {
      channel: "mychannel",
      messageId: data.id,
    };
  },
}
```

### Media Sending

```javascript
outbound: {
  sendMedia: async ({ cfg, to, text, mediaUrl, accountId }) => {
    const userId = to.replace(/^mychannel:/, "");
    const account = resolveAccount(cfg, accountId);

    // Check if URL is local file path
    const isLocalPath = mediaUrl.startsWith("/") || mediaUrl.startsWith("sandbox:");

    let mediaPayload;
    if (isLocalPath) {
      // Read local file and convert to base64
      const filePath = mediaUrl.replace(/^sandbox:\/{0,2}/, "/");
      const fileBuffer = await fs.readFile(filePath);
      const base64 = fileBuffer.toString("base64");
      const mimeType = detectMimeType(filePath);

      mediaPayload = {
        type: "image",
        base64: base64,
        mimeType: mimeType,
      };
    } else {
      // Use external URL
      mediaPayload = {
        type: "image",
        url: mediaUrl,
      };
    }

    const response = await fetch("https://api.example.com/messages", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${account.token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        to: userId,
        text: text,
        media: mediaPayload,
      }),
    });

    const data = await response.json();
    return {
      channel: "mychannel",
      messageId: data.id,
    };
  },
}
```

---

## Gateway Adapter

The gateway adapter starts and stops the message receiving service.

### Webhook-Based Gateway

```javascript
// Webhook targets registry
const webhookTargets = new Map();

function registerWebhookTarget(target) {
  const key = normalizeWebhookPath(target.path);
  webhookTargets.set(key, target);
  return () => webhookTargets.delete(key);
}

gateway: {
  startAccount: async (ctx) => {
    const account = ctx.account;

    logger.info("Gateway starting", { accountId: account.accountId });

    // Register webhook target for HTTP handler
    const unregister = registerWebhookTarget({
      path: account.webhookPath || "/webhooks/mychannel",
      account,
      config: ctx.cfg,
    });

    return {
      shutdown: async () => {
        logger.info("Gateway shutting down");
        unregister();
      },
    };
  },
}
```

### Polling-Based Gateway

```javascript
gateway: {
  startAccount: async (ctx) => {
    const account = ctx.account;
    let running = true;

    // Start polling thread
    const pollThread = async () => {
      while (running) {
        try {
          const messages = await pollForMessages(account);

          for (const msg of messages) {
            await processInboundMessage({
              message: msg,
              account,
              config: ctx.cfg,
            });
          }

          await sleep(1000); // Poll interval
        } catch (err) {
          logger.error("Polling error", { error: err.message });
          await sleep(5000); // Longer delay on error
        }
      }
    };

    pollThread(); // Don't await, let it run in background

    return {
      shutdown: async () => {
        running = false;
        logger.info("Gateway stopped");
      },
    };
  },
}
```

---

## Directory Adapter

The directory adapter provides user and group lookup.

```javascript
directory: {
  self: async () => {
    // Return bot's own info
    return {
      id: "bot_id",
      name: "Bot Name",
      kind: "user",
    };
  },

  listPeers: async () => {
    // Return list of users/chats
    return [
      { id: "user1", name: "User One", kind: "user" },
      { id: "user2", name: "User Two", kind: "user" },
    ];
  },

  listGroups: async () => {
    // Return list of groups/channels
    return [
      { id: "group1", name: "Group One", kind: "group" },
      { id: "group2", name: "Group Two", kind: "group" },
    ];
  },
}
```

---

## Status Adapter

The status adapter provides health and status information.

```javascript
status: {
  probe: async ({ cfg, accountId }) => {
    const account = resolveAccount(cfg, accountId);

    try {
      // Test API connectivity
      const response = await fetch("https://api.example.com/health", {
        headers: { "Authorization": `Bearer ${account.token}` },
      });

      return {
        ok: response.ok,
        message: response.ok ? "Connected" : `Error: ${response.status}`,
      };
    } catch (err) {
      return {
        ok: false,
        message: `Connection failed: ${err.message}`,
      };
    }
  },

  collectStatusIssues: ({ cfg, accountId, lastError }) => {
    const issues = [];

    const account = resolveAccount(cfg, accountId);
    if (!account) {
      issues.push({ kind: "config", message: "Account not configured" });
    }

    if (!account?.token) {
      issues.push({ kind: "config", message: "Token not configured" });
    }

    if (lastError) {
      issues.push({ kind: "error", message: lastError.message });
    }

    return issues;
  },
}
```

---

## Streaming Support

For channels that support streaming responses (like WeCom AI Bot).

### Stream Manager

```javascript
class StreamManager {
  constructor() {
    this.streams = new Map();
  }

  createStream(streamId) {
    this.streams.set(streamId, {
      content: "",
      finished: false,
      updatedAt: Date.now(),
      images: [],
    });
  }

  appendStream(streamId, content) {
    const stream = this.streams.get(streamId);
    if (stream && !stream.finished) {
      stream.content += content;
      stream.updatedAt = Date.now();
    }
  }

  replaceIfPlaceholder(streamId, content, placeholder) {
    const stream = this.streams.get(streamId);
    if (stream && stream.content.trim() === placeholder.trim()) {
      stream.content = content;
      stream.updatedAt = Date.now();
    } else if (stream) {
      this.appendStream(streamId, content);
    }
  }

  async finishStream(streamId) {
    const stream = this.streams.get(streamId);
    if (stream) {
      stream.finished = true;
      stream.updatedAt = Date.now();
    }
  }

  getStream(streamId) {
    return this.streams.get(streamId);
  }

  hasStream(streamId) {
    return this.streams.has(streamId);
  }

  deleteStream(streamId) {
    this.streams.delete(streamId);
  }
}

export const streamManager = new StreamManager();
```

---

## Common Patterns

### Message Deduplication

```javascript
const dedupeCache = createDedupeCache(60000); // 1 minute TTL

async function handleWebhook(data) {
  const messageId = data.id;

  if (dedupeCache.has(messageId)) {
    logger.debug("Duplicate message ignored", { messageId });
    return;
  }

  dedupeCache.add(messageId);

  // Process message...
}
```

### Signature Verification

```javascript
import crypto from "crypto";

function verifySignature(body, signature, secret) {
  const expectedSignature = crypto
    .createHmac("sha256", secret)
    .update(body)
    .digest("hex");

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// In webhook handler:
const signature = req.headers["x-signature"];
if (!verifySignature(body, signature, account.secret)) {
  res.writeHead(401);
  res.end("Unauthorized");
  return true;
}
```

### Group Mention Gating

```javascript
function shouldTriggerGroupResponse(content, config) {
  const groupConfig = config?.channels?.mychannel?.groupChat;

  if (!groupConfig?.requireMention) {
    return true; // No mention required
  }

  // Check for @mention
  const botMention = new RegExp(`@${config.botName}\\b`, "i");
  return botMention.test(content);
}

function extractGroupMessageContent(content, config) {
  // Remove @mention from content
  const botMention = new RegExp(`@${config.botName}\\s*`, "gi");
  return content.replace(botMention, "").trim();
}
```

### Dynamic Agent Routing

```javascript
function generateAgentId(kind, peerId) {
  return kind === "group"
    ? `mychannel-group-${peerId}`
    : `mychannel-dm-${peerId}`;
}

// In route resolution:
if (dynamicConfig.enabled) {
  const targetAgentId = generateAgentId(peerKind, peerId);
  route.agentId = targetAgentId;
  route.sessionKey = `agent:${targetAgentId}:${peerKind}:${peerId}`;
}
```

### Message Debouncing

```javascript
const DEBOUNCE_MS = 2000;
const messageBuffers = new Map();

function bufferMessage(streamKey, message, callback) {
  const existing = messageBuffers.get(streamKey);

  if (existing) {
    existing.messages.push(message);
    clearTimeout(existing.timer);
    existing.timer = setTimeout(() => flushBuffer(streamKey, callback), DEBOUNCE_MS);
  } else {
    messageBuffers.set(streamKey, {
      messages: [message],
      timer: setTimeout(() => flushBuffer(streamKey, callback), DEBOUNCE_MS),
    });
  }
}

function flushBuffer(streamKey, callback) {
  const buffer = messageBuffers.get(streamKey);
  if (!buffer) return;

  messageBuffers.delete(streamKey);

  // Merge messages
  const mergedContent = buffer.messages.map(m => m.content).join("\n");
  callback({ ...buffer.messages[0], content: mergedContent });
}
```
