# 🐍 Microservicio 4: Python 3.11 / FastAPI (IA, Agentes & MCP)

> **Ruta en Repositorio:** `backend/ms4-ia-mcp-python/`  
> **Puerto por Defecto:** `8000`  
> **Célula Responsable:** Perfil C (Grupo #27)  

---

## 🏛️ Estructura de Directorios (Metodología ICONIX)

```text
backend/ms4-ia-mcp-python/
├── app/
│   ├── boundaries/         # <<Boundary>> Routers FastAPI REST
│   │   ├── dl_vision_router.py
│   │   ├── ml_supervised_router.py
│   │   ├── ml_unsupervised_router.py
│   │   ├── agent_monitor_router.py
│   │   └── voice_mcp_router.py
│   ├── controls/           # <<Control>> Clases de Control Orquestadoras
│   │   ├── crash_vision_control.py
│   │   ├── supervised_ml_control.py
│   │   ├── unsupervised_fraud_control.py
│   │   ├── langgraph_autonomous_agent.py
│   │   └── voice_mcp_control.py
│   ├── entities/           # <<Entity>> Modelos Pydantic v2
│   │   ├── vision_dto.py
│   │   ├── supervised_dto.py
│   │   ├── unsupervised_dto.py
│   │   ├── agent_dto.py
│   │   └── voice_mcp_dto.py
│   ├── mcp_voice_reports/  # Módulos Especializados CU15
│   │   ├── security/       # OwaspAntiSqliGuard (Filtro AST + Regex)
│   │   ├── server/         # McpProtocolServer (4 Tools oficiales)
│   │   ├── stt/            # WhisperEngine (Decodificador acústico)
│   │   └── exporters/      # ExcelExporter, PdfExporter, WordExporter
│   ├── ml_artifacts/       # Modelos serializados (.h5, .joblib)
│   ├── ml_supervised/      # Script de entrenamiento Random Forest
│   └── main.py             # Entrada de FastAPI con CORS y Health Checks
├── artifacts/reports/      # Almacenamiento efímero de reportes compilados
└── tests/                  # Suite Pytest (40 tests unitarios e integrados)
```

---

## ⚙️ Tecnologías y Librerías Principales
- **Framework Web:** FastAPI 0.115 + Uvicorn + Pydantic v2.
- **Deep Learning:** TensorFlow 2.18 / Keras (CNN CrashNet para visión artificial).
- **Machine Learning:** Scikit-Learn 1.6 (Random Forest, K-Means, Isolation Forest).
- **Agentes Autónomos:** LangGraph 0.2 + LangChain Core.
- **Generación Documental:** OpenPyXL (Excel), ReportLab (PDF), Python-Docx (Word).
- **Bases de Datos:** Motor AsyncPG (PostgreSQL 16) y Motor AsyncIO (MongoDB 7).

---

## 🧪 Pruebas Automatizadas
Para ejecutar la suite completa de 40 pruebas de la célula C:
```bash
cd backend/ms4-ia-mcp-python
pytest tests/ -v
```
**Resultado:** `40 passed in 95.55s` (100% éxito).
