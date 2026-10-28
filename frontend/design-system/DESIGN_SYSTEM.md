# 🎨 Sistema de Diseño "Executive Precision" — AegisCore AI
> **Fuente Oficial:** Proyecto Google Stitch MCP `projects/9132956203380267795` (*Empresas de Seguros*)  
> **Alineación:** ICONIX Boundary Objects (CU01 a CU15)  
> **Tokens & Variables:** [tokens.json](file:///./tokens.json) | [variables.css](file:///./variables.css) | [tailwind.preset.js](file:///./tailwind.preset.js)

---

## 🏛️ Filosofía de Diseño: Modern Institutional Minimalism & Fintech Precision
El sistema de diseño **"Executive Precision"** está concebido para reconciliar flujos actuariales y corporativos de alta densidad con telemetría de modelos de Deep Learning e IA Autónoma:
- **Calm, High-Density Utility:** Interfaz estructurada que prioriza escaneo visual rápido, alta densidad de información numérica y comprensión instantánea sin distracciones ornamentales.
- **Cognitive Bifurcation:** Los flujos empresariales centrales (suscripción, pólizas, facturación) operan sobre tonos institucionales neutros (`#0F172A`, `#F8FAFC`), mientras que los motores de IA autónoma (telemetría de visión CNN, detección de fraude y orquestación MCP) resaltan mediante acentos cromáticos distintivos (`#4F46E5`, `#3F33D6`).
- **Absolute Confidence:** Contornos nítidos de 1px (hairline borders), micro-elevaciones y tipografía monoespaciada para códigos y telemetría.

---

## 🎨 Paleta de Colores Oficial

### 1. Colores de Marca y Flujo Principal
| Token | Valor Hex | Rol / Aplicación |
|---|---|---|
| `--color-primary` | `#005C55` | Acento principal, validación y certificación de cobertura. |
| `--color-primary-container` | `#0F766E` | Executive Teal. Botones principales, tabs activas, badges certificados. |
| `--color-on-primary` | `#FFFFFF` | Texto de alto contraste sobre contenedor primario. |
| `--color-primary-fixed` | `#9CF2E8` | Fondos de pills de estado autorizados. |
| `--color-institutional-anchor` | `#0F172A` | Deep Navy. Jerarquía visual superior, barras de navegación y métricas ejecutivas. |

### 2. Acento de Inteligencia Artificial & Telemetría MCP
| Token | Valor Hex | Rol / Aplicación |
|---|---|---|
| `--color-tertiary` | `#3F33D6` | Royal Indigo. Modelos neuronales y lógica predictiva. |
| `--color-tertiary-container` | `#5951EF` | Contenedores de inferencia en tiempo real. |
| `--color-ai-indigo` | `#4F46E5` | Acciones de agentes LangGraph, triggers de voz MCP y pulsos de estado. |
| `--color-ai-glow` | `rgba(79, 70, 229, 0.25)` | Halo de iluminación perimetral para paneles con inferencia activa. |

### 3. Superficies y Elevación
| Capa | Hex | Uso en UI |
|---|---|---|
| `Canvas Base (Ground 0)` | `#F8FAFC` / `#F8F9FF` | Fondo general de la aplicación, previene fatiga visual. |
| `Surface Lowest` | `#FFFFFF` | Superficie pura para tarjetas, tablas y formularios. |
| `Surface Container Low` | `#EFF4FF` | Fondo secundario para tablas y bloques agrupados. |
| `Surface Container High` | `#DCE9FF` | Fondos de contenedores interactivos y modales. |
| `Hairline Border` | `#E2E8F0` / `#CBD5E1` | Separadores estructurales de 1px. |

### 4. Semántica Operacional
- **Solvencia / Liquidado / Aprobado (`#10B981`):** Pólizas vigentes, siniestros sin fraude, dispersiones automáticas.
- **En Revisión Actuarial (`#D97706`):** Triaje con intervención humana, análisis de riesgo intermedio.
- **Fraude Anómalo / Crítico (`#BA1A1A` / `#E11D48`):** Anomalías detectadas por Isolation Forest, rechazos inmediatos.

---

## 🔤 Tríada Tipográfica Funcional

1. **Plus Jakarta Sans (Títulos y Métricas Ejecutivas):**
   - Geometría moderna y estatura ejecutiva sin redondez excesiva.
   - Usado en: Encabezados de página, contadores KPI, modales de confirmación y tarjetas de balance.
2. **Inter (Cuerpo y Formularios):**
   - Altura de 'x' optimizada para lectura en densidades de datos elevadas.
   - Usado en: Celdas de tablas, inputs de datos, transcripciones de voz y etiquetas contextuales.
3. **JetBrains Mono (Identidad Técnica y Telemetría):**
   - Cifras tabulares monoespaciadas (`font-variant-numeric: tabular-nums`).
   - Usado en: Códigos de póliza (`POL-VX-88390`), VIN de vehículos (`5YJYGDEE3RF89104`), códigos ICD-10, hashes SHA-256 de idempotencia y latencias.

---

## 📱 Pantallas y Vistas Extraídas de Google Stitch

Las 6 pantallas oficiales del proyecto han sido extraídas a archivos HTML autónomos listos para previsualización e integración en:
`frontend/design-system/screens/`

| Archivo HTML | Nombre en Stitch | Tipo | Casos de Uso ICONIX (Boundary) |
|---|---|---|---|
| [`ai-damage-inspector.html`](file:///frontend/design-system/screens/ai-damage-inspector.html) | AI Damage Inspector | Mobile | **CU07** (Inspección Móvil Peritos) / **CU11** (TensorFlow CNN Daños) |
| [`risk-fraud-sentinel.html`](file:///frontend/design-system/screens/risk-fraud-sentinel.html) | Risk & Fraud Sentinel | Mobile | **CU13** (Detección de Fraude Isolation Forest) |
| [`autonomous-agent-monitor.html`](file:///frontend/design-system/screens/autonomous-agent-monitor.html) | Autonomous Agent Monitor | Mobile | **CU14** (LangGraph Agente de Metas) / **CU15** (Voz MCP STT) |
| [`executive-kpi-dashboard.html`](file:///frontend/design-system/screens/executive-kpi-dashboard.html) | Executive KPI Dashboard | Mobile | **CU02** (Estado GraphQL) / **CU09** (Liquidación Transversal Saga) |
| [`actuarial-sales-prediction.html`](file:///frontend/design-system/screens/actuarial-sales-prediction.html) | Actuarial & Sales Prediction | Desktop | **CU12** (Random Forest Primas) / **CU13** (Segmentación K-Means) |
| [`deep-learning-damage-assessment.html`](file:///frontend/design-system/screens/deep-learning-damage-assessment.html) | Deep Learning Damage Assessment | Desktop | **CU11** (Visión Artificial Choques Desktop) |

---

## 🚀 Guía de Integración por Micro-Frontend / App

### 🅰️ Perfil A — React PWA (`frontend/mf2-clientes-react`)
1. Importar el preset en su `tailwind.config.js`:
   ```javascript
   module.exports = {
     presets: [require('../design-system/tailwind.preset.js')],
     content: ['./src/**/*.{js,jsx,ts,tsx}'],
   };
   ```
2. O bien incluir `frontend/design-system/variables.css` en su `src/index.css`:
   ```css
   @import '../design-system/variables.css';
   ```

### 🅱️ Perfil B — Flutter (`frontend/app-peritos-flutter`)
Configurar el tema en `lib/theme/app_theme.dart`:
```dart
import 'package:flutter/material.dart';

class AegisCoreTheme {
  static const Color primary = Color(0xFF005C55);
  static const Color primaryContainer = Color(0xFF0F766E);
  static const Color tertiary = Color(0xFF3F33D6);
  static const Color aiIndigo = Color(0xFF4F46E5);
  static const Color background = Color(0xFFF8F9FF);
  static const Color surfaceLowest = Color(0xFFFFFFFF);
  static const Color institutionalAnchor = Color(0xFF0F172A);
  static const Color solvency = Color(0xFF10B981);
  static const Color fraud = Color(0xFFBA1A1A);
}
```

### 🅲 Perfil C — Angular BI (`frontend/mf1-admin-angular`)
1. Referenciar `frontend/design-system/variables.css` en `angular.json` o `src/styles.css`.
2. Replicar los layouts de [`actuarial-sales-prediction.html`](file:///frontend/design-system/screens/actuarial-sales-prediction.html) y [`deep-learning-damage-assessment.html`](file:///frontend/design-system/screens/deep-learning-damage-assessment.html) conectando los gráficos de Chart.js / ECharts con las APIs de FastAPI (MS4).
