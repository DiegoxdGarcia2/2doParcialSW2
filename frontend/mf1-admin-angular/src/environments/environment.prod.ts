export const environment = {
  production: true,
  ms4: {
    baseUrl: 'http://127.0.0.1:8004',
    wsUrl: 'ws://127.0.0.1:8004',
    endpoints: {
      agent: 'http://127.0.0.1:8004/api/agent',
      agentWs: 'ws://127.0.0.1:8004/api/agent/ws',
      dlVision: 'http://127.0.0.1:8004/api/dl',
      voiceMcp: 'http://127.0.0.1:8004/api/v1/mcp',
      mlActuarial: 'http://127.0.0.1:8004/api/ml',
      mlUnsupervised: 'http://127.0.0.1:8004/api/ml/unsupervised',
      commercialAnalytics: 'http://127.0.0.1:8004/api/commercial',
      actuarialLoss: 'http://127.0.0.1:8004/api/actuarial/loss'
    }
  }
};
