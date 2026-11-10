const ms4Host = (typeof window !== 'undefined' && (window as any).__AEGIS_MS4_URL) || 'http://127.0.0.1:8004';
const ms4Ws = (typeof window !== 'undefined' && (window as any).__AEGIS_MS4_WS_URL) || 'ws://127.0.0.1:8004';

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
