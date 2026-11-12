const isLocalHost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const ms4Host = (typeof window !== 'undefined' && (window as any).__AEGIS_MS4_URL) || (isLocalHost ? 'http://127.0.0.1:8004' : 'https://aegiscore-ms4-ia-400568277774.us-central1.run.app');
const ms4Ws = (typeof window !== 'undefined' && (window as any).__AEGIS_MS4_WS_URL) || (isLocalHost ? 'ws://127.0.0.1:8004' : 'wss://aegiscore-ms4-ia-400568277774.us-central1.run.app');

export const environment = {
  production: true,
  ms4: {
    baseUrl: ms4Host,
    wsUrl: ms4Ws,
    endpoints: {
      agent: `${ms4Host}/api/agent`,
      agentWs: `${ms4Ws}/api/agent/ws`,
      dlVision: `${ms4Host}/api/dl`,
      voiceMcp: `${ms4Host}/api/v1/mcp`,
      mlActuarial: `${ms4Host}/api/ml`,
      mlUnsupervised: `${ms4Host}/api/ml/unsupervised`,
      commercialAnalytics: `${ms4Host}/api/commercial`,
      actuarialLoss: `${ms4Host}/api/actuarial/loss`
    }
  }
};
