const fs = require('fs');
const path = require('path');

const targetDir = path.join(__dirname, '..', 'frontend', 'design-system');
const screensDir = path.join(targetDir, 'screens');

if (!fs.existsSync(screensDir)) {
  fs.mkdirSync(screensDir, { recursive: true });
}

const screenMappings = [
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/39/output.txt',
    destFileName: 'ai-damage-inspector.html',
    title: 'AI Damage Inspector (Mobile Inspection)',
    type: 'MOBILE',
    cu: 'CU07 / CU11'
  },
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/51/output.txt',
    destFileName: 'risk-fraud-sentinel.html',
    title: 'Risk & Fraud Sentinel (Isolation Forest)',
    type: 'MOBILE',
    cu: 'CU13'
  },
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/53/output.txt',
    destFileName: 'autonomous-agent-monitor.html',
    title: 'Autonomous Agent Monitor (LangGraph / MCP)',
    type: 'MOBILE',
    cu: 'CU14 / CU15'
  },
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/55/output.txt',
    destFileName: 'executive-kpi-dashboard.html',
    title: 'Executive KPI Dashboard (BI & Solvency)',
    type: 'MOBILE',
    cu: 'CU02 / CU12'
  },
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/57/output.txt',
    destFileName: 'actuarial-sales-prediction.html',
    title: 'Actuarial & Sales Prediction (Desktop BI Angular)',
    type: 'DESKTOP',
    cu: 'CU12 / CU13'
  },
  {
    stepFile: 'C:/Users/david/.gemini/antigravity-ide/brain/738eeddd-2d97-4396-8850-d39a09d44be7/.system_generated/steps/59/output.txt',
    destFileName: 'deep-learning-damage-assessment.html',
    title: 'Deep Learning Damage Assessment (Desktop CNN)',
    type: 'DESKTOP',
    cu: 'CU11'
  }
];

screenMappings.forEach(mapping => {
  try {
    const rawData = fs.readFileSync(mapping.stepFile, 'utf8');
    const parsed = JSON.parse(rawData);
    if (parsed.html) {
      const destPath = path.join(screensDir, mapping.destFileName);
      fs.writeFileSync(destPath, parsed.html, 'utf8');
      console.log(`[SUCCESS] Extracted ${mapping.destFileName} (${parsed.html.length} bytes)`);
    } else {
      console.warn(`[WARN] No html property in ${mapping.stepFile}`);
    }
  } catch (err) {
    console.error(`[ERROR] Failed to extract ${mapping.destFileName}:`, err.message);
  }
});

console.log('All screen templates extracted successfully!');
