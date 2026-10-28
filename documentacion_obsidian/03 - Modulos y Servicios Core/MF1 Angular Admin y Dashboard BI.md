# 🅰️ Micro-Frontend 1: Angular 17+ Admin & BI Actuarial

> **Ruta en Repositorio:** `frontend/mf1-admin-angular/`  
> **Puerto por Defecto:** `4200`  
> **Célula Responsable:** Perfil C (Grupo #27)  

---

## 🎨 Sistema de Diseño: "Executive Precision"
- Basado en los tokens oficiales extraídos de **Google Stitch MCP** (`projects/9132956203380267795`).
- Paleta: *Executive Teal* (`#005C55`), *Deep Navy* (`#0F172A`), *AI Royal Indigo* (`#4F46E5`), *Alabaster* (`#F8FAFC`).
- Tipografías: `Plus Jakarta Sans` (Títulos/KPIs), `Inter` (Cuerpos), `JetBrains Mono` (Telemetría/Hashes).

---

## 🧭 Vistas y Rutas Implementadas (100% Nativas en Código)

| Ruta Angular | Caso de Uso | Descripción Visual | Gráficos y Componentes |
|---|---|---|---|
| `/ai-damage-inspector` | **CU11** | Visor de Peritaje Visual y Daños CNN | Drag & drop, Bounding Boxes dinámicos, heatmap Grad-CAM |
| `/actuarial-sales` | **CU12** | Tarificación Inteligente Random Forest | Sliders interactivos, Chart.js barras horizontales de Gini |
| `/risk-fraud-sentinel` | **CU13** | Detección de Fraude y Clusters | Scatter plot 2D/3D (K-Means), Radar de riesgo (Isolation Forest) |
| `/autonomous-agent-monitor` | **CU14** | Monitor de Agente Autónomo LangGraph | Grafo cíclico SVG animado, bitácora de skills, sensor de salud |
| `/voice-mcp-reports` | **CU15** | Reportes Dinámicos por Voz & Servidor MCP | Visualizador de onda de voz, simulador de ataques SQLi, descarga con SHA-256 |

---

## 🚀 Compilación y Despliegue
```bash
cd frontend/mf1-admin-angular
npm install
npm start          # Servidor de desarrollo en puerto 4200
npx ng build       # Compilación de bundle de producción
```
**Resultado:** Cero errores de TypeScript, paquete optimizado listo para producción.
