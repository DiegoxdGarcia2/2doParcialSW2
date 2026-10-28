import { Routes } from '@angular/router';
import { ActuarialDashboardComponent } from './features/actuarial-dashboard/actuarial-dashboard.component';
import { RiskFraudSentinelComponent } from './features/risk-fraud-sentinel/risk-fraud-sentinel.component';
import { AiDamageInspectorComponent } from './features/ai-damage-inspector/ai-damage-inspector.component';
import { AutonomousAgentMonitorComponent } from './features/autonomous-agent-monitor/autonomous-agent-monitor.component';
import { VoiceMcpReportsComponent } from './features/voice-mcp-reports/voice-mcp-reports.component';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'autonomous-agent-monitor',
    pathMatch: 'full'
  },
  {
    path: 'autonomous-agent-monitor',
    component: AutonomousAgentMonitorComponent
  },
  {
    path: 'ai-damage-inspector',
    component: AiDamageInspectorComponent
  },
  {
    path: 'risk-fraud-sentinel',
    component: RiskFraudSentinelComponent
  },
  {
    path: 'actuarial-dashboard',
    component: ActuarialDashboardComponent
  },
  {
    path: 'voice-mcp-reports',
    component: VoiceMcpReportsComponent
  },
  {
    path: '**',
    redirectTo: 'autonomous-agent-monitor'
  }
];

