# Testing Guide

This document provides a comprehensive guide for testing OpenClaw channel plugins.

## Table of Contents

- [Test Framework](#test-framework)
- [Mock Runtime](#mock-runtime)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Testing Patterns](#testing-patterns)

---

## Test Framework

We use Node.js built-in test framework (`node:test`).

### Running Tests

```bash
# Run all tests
npm test

# Run specific test file
node --test tests/channel.test.js

# Run with watch mode
node --test --watch tests/*.test.js
```

### Test File Structure

```javascript
import { describe, it, beforeEach, afterEach } from "node:test";
import assert from "node:assert";

describe("Feature Name", () => {
  beforeEach(() => {
    // Setup
  });

  afterEach(() => {
    // Cleanup
  });

  it("should do something", () => {
    // Test implementation
    assert.strictEqual(actual, expected);
  });
});
```

---

## Mock Runtime

The mock runtime simulates OpenClaw's core functionality for isolated testing.

### Creating Mock Runtime

```javascript
import { createMockRuntime, createMockApi } from "./mock-runtime.js";

const mockRuntime = createMockRuntime({
  config: {
    channels: {
      mychannel: {
        enabled: true,
        token: "test-token",
      },
    },
  },
});

const mockApi = createMockApi(mockRuntime);
```

### Customizing Mock Behavior

```javascript
const mockRuntime = createMockRuntime({
  // Override route resolution
  resolveAgentRoute: ({ peer }) => ({
    agentId: "test-agent",
    sessionKey: `test:${peer.kind}:${peer.id}`,
    accountId: "test-account",
  }),

  // Override reply dispatch
  dispatchReplyWithBufferedBlockDispatcher: async ({ ctx, dispatcherOptions }) => {
    // Custom mock behavior
    await dispatcherOptions.deliver(
      { text: "Custom mock response" },
      { kind: "final" }
    );
  },
});
```

### Mock HTTP Objects

```javascript
import { createMockRequest, createMockResponse } from "./mock-runtime.js";

// Create mock request
const req = createMockRequest({
  url: "/webhooks/mychannel",
  method: "POST",
  body: { type: "message", content: "Hello" },
  headers: { "x-signature": "abc123" },
});

// Create mock response
const res = createMockResponse();

// Use handler
await httpHandler(req, res);

// Check results
assert.strictEqual(res._getStatusCode(), 200);
assert.deepStrictEqual(res._getJSON(), { status: "ok" });
```

---

## Unit Tests

### Config Adapter Tests

```javascript
describe("config adapter", () => {
  it("should list account IDs correctly", () => {
    const ids = channelPlugin.config.listAccountIds(mockConfig);
    assert.deepStrictEqual(ids, ["default"]);
  });

  it("should resolve account correctly", () => {
    const account = channelPlugin.config.resolveAccount(mockConfig, "default");
    assert.strictEqual(account.enabled, true);
    assert.strictEqual(account.token, "test-token");
  });

  it("should return null for disabled channel", () => {
    mockConfig.channels.mychannel.enabled = false;
    const ids = channelPlugin.config.listAccountIds(mockConfig);
    assert.deepStrictEqual(ids, []);
  });

  it("should set account enabled status", () => {
    const cfg = { ...mockConfig };
    const result = channelPlugin.config.setAccountEnabled({
      cfg,
      accountId: "default",
      enabled: false,
    });
    assert.strictEqual(result.channels.mychannel.enabled, false);
  });
});
```

### Outbound Adapter Tests

```javascript
describe("outbound adapter", () => {
  it("should send text message", async () => {
    // Mock fetch if needed
    global.fetch = async () => ({
      ok: true,
      json: async () => ({ id: "msg_123" }),
    });

    const result = await channelPlugin.outbound.sendText({
      cfg: mockConfig,
      to: "mychannel:user123",
      text: "Hello!",
      accountId: "default",
    });

    assert.strictEqual(result.channel, "mychannel");
    assert.ok(result.messageId);
  });

  it("should strip channel prefix", async () => {
    let capturedTo = null;

    global.fetch = async (url, options) => {
      const body = JSON.parse(options.body);
      capturedTo = body.to;
      return { ok: true, json: async () => ({ id: "msg_123" }) };
    };

    await channelPlugin.outbound.sendText({
      cfg: mockConfig,
      to: "mychannel:user123",
      text: "Test",
      accountId: "default",
    });

    assert.strictEqual(capturedTo, "user123");
  });
});
```

### Gateway Adapter Tests

```javascript
describe("gateway adapter", () => {
  it("should start and shutdown gateway", async () => {
    const gateway = await channelPlugin.gateway.startAccount({
      account: createMockAccount(),
      cfg: mockConfig,
    });

    assert.ok(gateway);
    assert.ok(gateway.shutdown);

    await gateway.shutdown();
  });
});
```

---

## Integration Tests

### Webhook Handler Tests

```javascript
describe("webhook handler", () => {
  it("should handle valid POST request", async () => {
    const req = createMockRequest({
      url: "/webhooks/mychannel",
      method: "POST",
      body: {
        type: "message",
        from: "user123",
        content: "Hello",
      },
    });
    const res = createMockResponse();

    const handled = await httpHandler(req, res);

    assert.strictEqual(handled, true);
    assert.strictEqual(res._getStatusCode(), 200);
  });

  it("should reject invalid path", async () => {
    const req = createMockRequest({
      url: "/other/path",
      method: "POST",
      body: {},
    });
    const res = createMockResponse();

    const handled = await httpHandler(req, res);

    assert.strictEqual(handled, false);
  });

  it("should handle invalid JSON", async () => {
    const req = {
      url: "/webhooks/mychannel",
      method: "POST",
      headers: {},
      [Symbol.asyncIterator]: async function* () {
        yield Buffer.from("not valid json");
      },
    };
    const res = createMockResponse();

    await httpHandler(req, res);

    assert.strictEqual(res._getStatusCode(), 400);
  });
});
```

### Message Processing Tests

```javascript
describe("message processing", () => {
  it("should process text message correctly", async () => {
    let deliveredPayload = null;

    const runtime = createMockRuntime({
      dispatchReplyWithBufferedBlockDispatcher: async ({ ctx, dispatcherOptions }) => {
        await dispatcherOptions.deliver(
          { text: "Test response" },
          { kind: "final" }
        );
        deliveredPayload = ctx;
      },
    });

    await processInboundMessage({
      message: {
        fromUser: "user123",
        content: "Hello",
        chatType: "single",
      },
      account: createMockAccount(),
      config: mockConfig,
    });

    assert.ok(deliveredPayload);
    assert.strictEqual(deliveredPayload.SenderId, "user123");
  });
});
```

---

## Testing Patterns

### Mocking Fetch

```javascript
// Before tests
let originalFetch;

beforeEach(() => {
  originalFetch = global.fetch;
});

afterEach(() => {
  global.fetch = originalFetch;
});

// In test
it("should call API correctly", async () => {
  let calledUrl = null;
  let calledOptions = null;

  global.fetch = async (url, options) => {
    calledUrl = url;
    calledOptions = options;
    return {
      ok: true,
      json: async () => ({ id: "123" }),
    };
  };

  await someFunction();

  assert.strictEqual(calledUrl, "https://api.example.com/endpoint");
  assert.strictEqual(calledOptions.method, "POST");
});
```

### Testing Async Errors

```javascript
it("should throw on API error", async () => {
  global.fetch = async () => ({
    ok: false,
    status: 500,
    text: async () => "Internal Server Error",
  });

  await assert.rejects(
    async () => await channelPlugin.outbound.sendText({
      cfg: mockConfig,
      to: "user123",
      text: "Test",
      accountId: "default",
    }),
    { message: /API error/ }
  );
});
```

### Testing with Delays

```javascript
it("should handle debouncing", async () => {
  const messages = [];

  const callback = (msg) => messages.push(msg);

  bufferMessage("key1", { content: "msg1" }, callback);
  bufferMessage("key1", { content: "msg2" }, callback);

  // Wait for debounce
  await sleep(2500);

  // Should have merged messages
  assert.strictEqual(messages.length, 1);
  assert.ok(messages[0].content.includes("msg1"));
  assert.ok(messages[0].content.includes("msg2"));
});
```

### Testing Event Handlers

```javascript
it("should call deliver callback", async () => {
  let deliverCalled = false;
  let deliveredPayload = null;

  const runtime = createMockRuntime({
    dispatchReplyWithBufferedBlockDispatcher: async ({ dispatcherOptions }) => {
      await dispatcherOptions.deliver(
        { text: "Response" },
        { kind: "block" }
      );
    },
  });

  // ... test code ...

  assert.ok(deliverCalled);
});
```

### Snapshot Testing (Manual)

```javascript
it("should format message correctly", () => {
  const formatted = formatMessage({
    from: "user123",
    content: "Hello",
    timestamp: 1700000000000,
  });

  // Compare with expected output
  const expected = {
    from: "user123",
    text: "Hello",
    time: "2023-11-14T22:13:20.000Z",
  };

  assert.deepStrictEqual(formatted, expected);
});
```

---

## Test Coverage Checklist

Use this checklist to ensure comprehensive testing:

### Config Adapter
- [ ] listAccountIds returns correct IDs
- [ ] listAccountIds returns empty for disabled channel
- [ ] resolveAccount returns correct account
- [ ] resolveAccount returns null for missing config
- [ ] setAccountEnabled updates config
- [ ] deleteAccount removes config

### Outbound Adapter
- [ ] sendText sends to correct recipient
- [ ] sendText strips channel prefix
- [ ] sendText returns message ID
- [ ] sendText handles API errors
- [ ] sendMedia handles images
- [ ] sendMedia handles files

### Gateway Adapter
- [ ] startAccount initializes correctly
- [ ] shutdown cleans up resources
- [ ] Multiple accounts work correctly

### Webhook Handler
- [ ] Handles correct path
- [ ] Rejects incorrect path
- [ ] Handles POST requests
- [ ] Rejects invalid methods
- [ ] Parses JSON body
- [ ] Rejects invalid JSON
- [ ] Verifies signature (if applicable)
- [ ] Handles duplicate messages

### Message Processing
- [ ] Processes direct messages
- [ ] Processes group messages
- [ ] Handles media attachments
- [ ] Routes to correct agent
- [ ] Creates correct session key
