/**
 * Mock Runtime for Testing
 *
 * This file provides a mock OpenClaw runtime for testing plugins
 * without requiring a full OpenClaw installation.
 */

/**
 * Create a mock runtime for testing
 * @param {Object} overrides - Override default behavior
 */
export function createMockRuntime(overrides = {}) {
  const defaultConfig = {
    channels: {
      {{CHANNEL_ID}}: {
        enabled: true,
        // TODO: Add default channel config
      },
    },
    agents: {
      list: [{ id: "main" }],
    },
    session: {
      store: { path: "/tmp/sessions" },
    },
  };

  let currentConfig = { ...defaultConfig, ...overrides.config };
  let sessionMeta = {};

  return {
    channel: {
      routing: {
        resolveAgentRoute: overrides.resolveAgentRoute || (({ peer }) => ({
          agentId: "main",
          sessionKey: `agent:main:${peer.kind}:${peer.id}`,
          accountId: "default",
        })),
      },
      reply: {
        dispatchReplyWithBufferedBlockDispatcher:
          overrides.dispatchReplyWithBufferedBlockDispatcher ||
          (async ({ ctx, dispatcherOptions }) => {
            // Mock AI response
            await dispatcherOptions.deliver(
              { text: "Mock AI response" },
              { kind: "final" }
            );
          }),
        resolveEnvelopeFormatOptions: () => ({}),
        formatAgentEnvelope: ({ body }) => body,
        finalizeInboundContext: (ctx) => ctx,
      },
      session: {
        resolveStorePath: () => "/tmp/sessions",
        readSessionUpdatedAt: () => null,
        recordSessionMetaFromInbound: async ({ sessionKey, ctx }) => {
          sessionMeta[sessionKey] = {
            lastUpdated: Date.now(),
            senderId: ctx.SenderId,
          };
        },
      },
    },
    config: {
      loadConfig: () => currentConfig,
      writeConfigFile: async (cfg) => {
        currentConfig = cfg;
      },
    },
    // Test helpers
    _getConfig: () => currentConfig,
    _getSessionMeta: () => sessionMeta,
    _resetSessionMeta: () => {
      sessionMeta = {};
    },
  };
}

/**
 * Create a mock plugin API for testing
 * @param {Object} runtime - Mock runtime
 */
export function createMockApi(runtime = createMockRuntime()) {
  const registeredChannels = [];
  const registeredHandlers = [];

  return {
    id: "{{CHANNEL_ID}}-test",
    name: "{{CHANNEL_LABEL}} Test Plugin",
    config: runtime.config.loadConfig(),
    runtime,
    logger: {
      info: console.log,
      warn: console.warn,
      error: console.error,
      debug: process.env.DEBUG ? console.debug : () => {},
    },
    registerChannel: (registration) => {
      registeredChannels.push(registration);
    },
    registerHttpHandler: (handler) => {
      registeredHandlers.push(handler);
    },
    // Test accessors
    _getRegisteredChannels: () => registeredChannels,
    _getRegisteredHandlers: () => registeredHandlers,
  };
}

/**
 * Create mock HTTP request
 * @param {Object} options - Request options
 */
export function createMockRequest(options = {}) {
  const {
    url = "/webhooks/{{CHANNEL_ID}}",
    method = "POST",
    body = {},
    headers = {},
  } = options;

  const bodyStr = typeof body === "string" ? body : JSON.stringify(body);

  return {
    url,
    method,
    headers: {
      "content-type": "application/json",
      ...headers,
    },
    [Symbol.asyncIterator]: async function* () {
      yield Buffer.from(bodyStr);
    },
  };
}

/**
 * Create mock HTTP response
 */
export function createMockResponse() {
  let statusCode = null;
  let headers = {};
  let body = null;

  return {
    writeHead: (code, hdrs = {}) => {
      statusCode = code;
      headers = { ...headers, ...hdrs };
    },
    end: (data) => {
      body = data;
    },
    // Test accessors
    _getStatusCode: () => statusCode,
    _getHeaders: () => headers,
    _getBody: () => body,
    _getJSON: () => {
      try {
        return JSON.parse(body);
      } catch {
        return null;
      }
    },
  };
}

/**
 * Create mock account
 */
export function createMockAccount(overrides = {}) {
  return {
    id: "default",
    accountId: "default",
    enabled: true,
    // TODO: Add channel-specific account properties
    ...overrides,
  };
}
