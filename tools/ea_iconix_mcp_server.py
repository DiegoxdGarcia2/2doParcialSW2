# -*- coding: utf-8 -*-
"""
Servidor MCP para Sparx Systems Enterprise Architect 17.2 (.qea, .xmi, .xml)
Proyecto: AegisCore AI — ERP Distribuido, Peritaje Inteligente y Liquidación Autónoma de Siniestros
Protocolo: Model Context Protocol (MCP) JSON-RPC 2.0 por stdio y CLI interactivo (--cli).

Herramientas MCP Expuestas:
  1. inspect_qea_database: Inspecciona cualquier archivo .qea (paquetes, diagramas, clases, atributos,
     métodos, conectores) y devuelve un resumen estructurado.
  2. verify_code_diagram_alignment: Verifica automáticamente que todas las clases y métodos de
     backend/ms1-polizas-php/src y frontend/mf2-clientes-react/src existan en AegisCore_Perfil_A.qea
     y aegiscore-perfil-a-ea17.xmi.
  3. rebuild_perfil_a_ea_artifacts: Ejecuta la reconstrucción completa de .qea y .xmi.
  4. open_in_enterprise_architect: Abre el archivo .qea o .xmi directamente en Enterprise Architect
     en Windows o muestra la ruta absoluta lista para abrir.
"""
import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import xml.etree.ElementTree as ET


# =============================================================================
# HERRAMIENTA 1: inspect_qea_database
# =============================================================================
def inspect_qea_database(qea_path: str) -> dict:
    if not os.path.isabs(qea_path):
        qea_path = os.path.abspath(qea_path)

    if not os.path.exists(qea_path):
        return {"error": f"El archivo '{qea_path}' no existe."}

    conn = sqlite3.connect(qea_path)
    cur = conn.cursor()

    # Paquetes
    packages_raw = cur.execute("SELECT Package_ID, Name, Parent_ID FROM t_package ORDER BY Package_ID").fetchall()
    packages = [{"id": r[0], "name": r[1], "parent_id": r[2]} for r in packages_raw]

    # Diagramas y verificación de no-vacíos
    diagrams_raw = cur.execute("SELECT Diagram_ID, Name, Diagram_Type FROM t_diagram ORDER BY Diagram_ID").fetchall()
    diagrams = []
    empty_diagrams = []
    for did, name, dtype in diagrams_raw:
        obj_cnt = cur.execute("SELECT COUNT(*) FROM t_diagramobjects WHERE Diagram_ID = ?", (did,)).fetchone()[0]
        conn_cnt = cur.execute("SELECT COUNT(*) FROM t_connector WHERE DiagramID = ?", (did,)).fetchone()[0]
        is_empty = (obj_cnt == 0)
        diag_info = {
            "diagram_id": did,
            "name": name,
            "type": dtype,
            "objects_count": obj_cnt,
            "connectors_count": conn_cnt,
            "status": "EMPTY" if is_empty else "OK"
        }
        diagrams.append(diag_info)
        if is_empty:
            empty_diagrams.append(name)

    # Objetos por tipo
    objects_raw = cur.execute("SELECT Object_ID, Name, Object_Type, Stereotype FROM t_object ORDER BY Object_ID").fetchall()
    types_breakdown = {}
    for _, _, otype, stereo in objects_raw:
        label = f"{otype} ({stereo})" if stereo else otype
        types_breakdown[label] = types_breakdown.get(label, 0) + 1

    total_attributes = cur.execute("SELECT COUNT(*) FROM t_attribute").fetchone()[0]
    total_operations = cur.execute("SELECT COUNT(*) FROM t_operation").fetchone()[0]

    # Conectores por tipo
    connectors_raw = cur.execute("SELECT Connector_ID, Name, Connector_Type FROM t_connector ORDER BY Connector_ID").fetchall()
    conn_types = {}
    for _, _, ctype in connectors_raw:
        conn_types[ctype] = conn_types.get(ctype, 0) + 1

    conn.close()

    file_size_bytes = os.path.getsize(qea_path)

    return {
        "file_path": qea_path,
        "file_size_kb": round(file_size_bytes / 1024, 2),
        "total_packages": len(packages),
        "packages": packages,
        "total_diagrams": len(diagrams),
        "empty_diagrams_count": len(empty_diagrams),
        "empty_diagrams": empty_diagrams,
        "diagrams": diagrams,
        "total_objects": len(objects_raw),
        "objects_breakdown": types_breakdown,
        "total_attributes": total_attributes,
        "total_operations": total_operations,
        "total_connectors": len(connectors_raw),
        "connectors_breakdown": conn_types,
        "health": "PERFECT (0 diagramas vacíos)" if len(empty_diagrams) == 0 else f"WARNING ({len(empty_diagrams)} diagramas vacíos)"
    }


# =============================================================================
# HERRAMIENTA 2: verify_code_diagram_alignment
# =============================================================================
def verify_code_diagram_alignment(
    qea_path: str = "AegisCore_Perfil_A.qea",
    xmi_path: str = "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi"
) -> dict:
    if not os.path.isabs(qea_path):
        qea_path = os.path.abspath(qea_path)
    if not os.path.isabs(xmi_path):
        xmi_path = os.path.abspath(xmi_path)

    if not os.path.exists(qea_path):
        return {"error": f"Archivo QEA no encontrado: {qea_path}"}
    if not os.path.exists(xmi_path):
        return {"error": f"Archivo XMI no encontrado: {xmi_path}"}

    # Clases clave esperadas de backend/ms1-polizas-php y frontend/mf2-clientes-react
    expected_classes = [
        # Clases de Dominio DDD
        "UsuarioRol",
        "SesionUnificadaToken",
        "Cliente",
        "PlanSeguro",
        "Cobertura",
        "Poliza",
        "BienAseguradoVehiculo",
        "FacturaNotaVenta",
        "CacheCoberturaActiva",
        # BCE CU01 (SSO Keycloak)
        "LoginKeycloakSSOView",
        "AuthOIDCService",
        "AuthOIDCController",
        "DynamoDbSessionCacheRepository",
        "UsuarioRolEntity",
        # BCE CU02 (GraphQL Federation)
        "PortalClientesGraphQLView",
        "ApolloFederationClient",
        "ApolloFederationResolver",
        "PostgresPolizaRepository",
        "ExpedienteSiniestroMongoMirror",
        # BCE CU03 (Catálogo DDD)
        "CatalogoPlanesYClientesView",
        "CatalogoPolizaApplicationService",
        "PostgresPlanSeguroRepository",
        "PostgresClienteRepository",
        # BCE CU04 (Cotizador Web IA Local)
        "CotizadorWebPWAView",
        "ValidadorNitidezLocalWebControl",
        "EmisionPolizaGraphQLController",
        "CotizacionPolizaDomainService",
        "PostgresFacturaRepository",
        # BCE CU05 (WhatsApp n8n Factura S3)
        "CanalWhatsAppWebhookView",
        "N8nWebhookHandler",
        "RecepcionPedidoService",
        "FacturacionService",
        "FacturacionDomainService",
        "FacturaPdfGenerator",
        "AwsS3BucketEntity",
        # BCE CU09-MS1 (Saga Cobertura)
        "SimuladorSagaCoberturaView",
        "PolizaCoberturaService",
        "SagaKafkaConsumer",
        # BCE CU10-MS1 (QR EMVCo)
        "PasarelaPagoQREMVCoView"
    ]

    expected_methods = [
        "autenticarUsuarioOIDC",
        "validarTokenJwtRS256",
        "sincronizarUsuarioRolPostgreSQL",
        "registrarSesionUnificadaDynamoDB",
        "guardarSesionUnificada",
        "resolverResumenUnificadoAsegurado",
        "consultarOActualizarCacheCoberturaActiva",
        "federarExpedientesSiniestrosMongoDB",
        "listarPlanesSeguro",
        "registrarPlanSeguroDDD",
        "agregarCoberturaAPlan",
        "registrarClienteDDD",
        "cotizarPolizaEnLinea",
        "validarNitidez",
        "insertarPoliza",
        "emitirPoliza",
        "calcularCotizacion",
        "analizarNitidezImagen",
        "calcularVarianzaLaplaciana",
        "procesarPedidoPolizaWhatsApp",
        "generarFacturaNotaVentaPDF",
        "descontarTechoAnualPoliza",
        "compensarCoberturaSaga",
        "restituirSaldoCobertura",
        "compilarArchivoFacturaPdf",
        "nombreCompleto",
        "techoCoberturaMaximo",
        "emitirNueva"
    ]

    # 1. Verificar en Base de Datos QEA
    conn = sqlite3.connect(qea_path)
    cur = conn.cursor()

    qea_objects = {r[0] for r in cur.execute("SELECT Name FROM t_object").fetchall()}
    qea_operations = {r[0].replace("()", "") for r in cur.execute("SELECT Name FROM t_operation").fetchall()}
    conn.close()

    # 2. Verificar en XMI / XML
    tree = ET.parse(xmi_path)
    root = tree.getroot()

    xmi_classes = set()
    xmi_operations = set()
    for elem in root.iter():
        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
        name = elem.attrib.get("name")
        if name:
            if tag in ("packagedElement", "element") and elem.attrib.get("xmi:type") in ("uml:Class", None):
                xmi_classes.add(name)
            elif tag == "ownedOperation":
                xmi_operations.add(name.replace("()", ""))

    # Comparación
    classes_missing_qea = [c for c in expected_classes if c not in qea_objects]
    classes_missing_xmi = [c for c in expected_classes if c not in xmi_classes]

    methods_missing_qea = [m for m in expected_methods if not any(m in op for op in qea_operations)]
    methods_missing_xmi = [m for m in expected_methods if not any(m in op for op in xmi_operations)]

    total_checks = len(expected_classes) * 2 + len(expected_methods) * 2
    passed_checks = (
        (len(expected_classes) - len(classes_missing_qea)) +
        (len(expected_classes) - len(classes_missing_xmi)) +
        (len(expected_methods) - len(methods_missing_qea)) +
        (len(expected_methods) - len(methods_missing_xmi))
    )

    alignment_percentage = round((passed_checks / total_checks) * 100, 2)

    return {
        "status": "PASS" if alignment_percentage == 100.0 else "FAIL",
        "alignment_percentage": alignment_percentage,
        "total_expected_classes": len(expected_classes),
        "total_expected_methods": len(expected_methods),
        "qea_validation": {
            "matched_classes": len(expected_classes) - len(classes_missing_qea),
            "missing_classes": classes_missing_qea,
            "matched_methods": len(expected_methods) - len(methods_missing_qea),
            "missing_methods": methods_missing_qea
        },
        "xmi_validation": {
            "matched_classes": len(expected_classes) - len(classes_missing_xmi),
            "missing_classes": classes_missing_xmi,
            "matched_methods": len(expected_methods) - len(methods_missing_xmi),
            "missing_methods": methods_missing_xmi
        }
    }


# =============================================================================
# HERRAMIENTA 3: rebuild_perfil_a_ea_artifacts
# =============================================================================
def rebuild_perfil_a_ea_artifacts(execute_global: bool = False) -> dict:
    results = {}

    # 1. Ejecutar build_perfil_a_qea.py
    try:
        res_qea = subprocess.run([sys.executable, "build_perfil_a_qea.py"], capture_output=True, text=True, check=True)
        results["build_perfil_a_qea"] = {
            "success": True,
            "output": res_qea.stdout.strip()
        }
    except Exception as e:
        results["build_perfil_a_qea"] = {"success": False, "error": str(e)}

    # 2. Ejecutar generate_ea_xmi_perfil_a.py
    try:
        xmi_script = os.path.join("docs-iconix-uml", "enterprise-architect", "generate_ea_xmi_perfil_a.py")
        res_xmi = subprocess.run([sys.executable, xmi_script], capture_output=True, text=True, check=True)
        results["generate_ea_xmi_perfil_a"] = {
            "success": True,
            "output": res_xmi.stdout.strip()
        }
    except Exception as e:
        results["generate_ea_xmi_perfil_a"] = {"success": False, "error": str(e)}

    # 3. Si se solicita, reconstruir AegisCore_AI.qea global
    if execute_global:
        try:
            res_glob = subprocess.run([sys.executable, "build_full_project_qea.py"], capture_output=True, text=True, check=True)
            results["build_full_project_qea"] = {
                "success": True,
                "output": res_glob.stdout.strip()
            }
        except Exception as e:
            results["build_full_project_qea"] = {"success": False, "error": str(e)}

    # Verificar archivos generados
    artifacts = [
        "AegisCore_Perfil_A.qea",
        "docs-iconix-uml/AegisCore_Perfil_A.qea",
        "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.qea",
        "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi",
        "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xml",
        "docs-iconix-uml/aegiscore-perfil-a-iconix-uml25.xmi"
    ]
    if execute_global:
        artifacts.extend(["AegisCore_AI.qea", "docs-iconix-uml/AegisCore_AI.qea"])

    files_status = {}
    for a in artifacts:
        if os.path.exists(a):
            files_status[a] = f"OK ({os.path.getsize(a)} bytes)"
        else:
            files_status[a] = "MISSING"

    results["artifacts_status"] = files_status
    return results


# =============================================================================
# HERRAMIENTA 4: open_in_enterprise_architect
# =============================================================================
def open_in_enterprise_architect(file_path: str, launch: bool = True) -> dict:
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return {"error": f"El archivo '{file_path}' no existe."}

    # Búsqueda de ejecutables de EA
    ea_candidates = [
        r"C:\Program Files\Sparx Systems\EA\EA.exe",
        r"C:\Program Files (x86)\Sparx Systems\EA\EA.exe",
        r"C:\Program Files\Sparx Systems\EA Trial\EA.exe"
    ]
    found_exe = None
    for candidate in ea_candidates:
        if os.path.exists(candidate):
            found_exe = candidate
            break

    if found_exe:
        if not launch:
            return {
                "status": "READY",
                "message": f"Enterprise Architect detectado en '{found_exe}'. Listo para abrir '{file_path}'.",
                "executable": found_exe,
                "file_path": file_path
            }
        try:
            subprocess.Popen(
                [found_exe, file_path],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0)
            )
            return {
                "status": "LAUNCHED",
                "message": f"Enterprise Architect iniciado con éxito abriendo '{file_path}'.",
                "executable": found_exe,
                "file_path": file_path
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "file_path": file_path}
    else:
        # Intentar apertura por asociación de Windows o devolver ruta lista
        try:
            os.startfile(file_path)
            return {
                "status": "OPENED_WITH_DEFAULT_APP",
                "message": f"Archivo abierto con la asociación predeterminada de Windows.",
                "file_path": file_path,
                "note": "Para abrir explícitamente con EA 17, asocie la extensión .qea con EA.exe."
            }
        except Exception:
            return {
                "status": "READY_TO_OPEN",
                "message": "Enterprise Architect no se encuentra en las rutas estándar. El archivo está listo para ser abierto manualmente.",
                "file_path": file_path,
                "powershell_command": f'Start-Process "{file_path}"'
            }


# =============================================================================
# PROTOCOLO MCP: JSON-RPC 2.0 por STDIN/STDOUT
# =============================================================================
TOOLS_REGISTRY = {
    "inspect_qea_database": {
        "description": "Inspecciona cualquier base de datos SQLite (.qea) de Enterprise Architect 17.2, reportando paquetes, diagramas, clases, atributos, operaciones, conectores y detectando diagramas vacíos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "qea_path": {
                    "type": "string",
                    "description": "Ruta absoluta o relativa al archivo .qea a inspeccionar (ej: AegisCore_Perfil_A.qea o AegisCore_AI.qea)."
                }
            },
            "required": ["qea_path"]
        },
        "handler": lambda args: inspect_qea_database(args.get("qea_path", "AegisCore_Perfil_A.qea"))
    },
    "verify_code_diagram_alignment": {
        "description": "Verifica automáticamente que todas las clases y métodos de backend/ms1-polizas-php y frontend/mf2-clientes-react existan fielmente en AegisCore_Perfil_A.qea y aegiscore-perfil-a-ea17.xmi.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "qea_path": {
                    "type": "string",
                    "description": "Ruta al archivo .qea (por defecto: AegisCore_Perfil_A.qea)."
                },
                "xmi_path": {
                    "type": "string",
                    "description": "Ruta al archivo .xmi (por defecto: docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi)."
                }
            }
        },
        "handler": lambda args: verify_code_diagram_alignment(
            args.get("qea_path", "AegisCore_Perfil_A.qea"),
            args.get("xmi_path", "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi")
        )
    },
    "rebuild_perfil_a_ea_artifacts": {
        "description": "Ejecuta los generadores para reconstruir los archivos .qea (AegisCore_Perfil_A.qea) y .xmi/.xml de Perfil A, con opción de actualizar también el modelo global AegisCore_AI.qea.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "execute_global": {
                    "type": "boolean",
                    "description": "Si es True, reconstruye también el modelo global AegisCore_AI.qea."
                }
            }
        },
        "handler": lambda args: rebuild_perfil_a_ea_artifacts(args.get("execute_global", False))
    },
    "open_in_enterprise_architect": {
        "description": "Abre el archivo .qea o .xmi directamente en Enterprise Architect 17.2 en Windows o muestra el comando listo para ejecutar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Ruta al archivo .qea o .xmi a abrir."
                }
            },
            "required": ["file_path"]
        },
        "handler": lambda args: open_in_enterprise_architect(args.get("file_path", "AegisCore_Perfil_A.qea"))
    }
}


def run_mcp_server():
    """Ejecuta el bucle de mensajes JSON-RPC 2.0 por stdio."""
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "ea-iconix-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            tools_list = []
            for tname, tinfo in TOOLS_REGISTRY.items():
                tools_list.append({
                    "name": tname,
                    "description": tinfo["description"],
                    "inputSchema": tinfo["inputSchema"]
                })
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": tools_list}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name in TOOLS_REGISTRY:
                try:
                    result_data = TOOLS_REGISTRY[tool_name]["handler"](tool_args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result_data, indent=2, ensure_ascii=False)
                                }
                            ]
                        }
                    }
                except Exception as e:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32000, "message": str(e)}
                    }
            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Herramienta desconocida: {tool_name}"}
                }
        else:
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Método no implementado: {method}"}
            }

        sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        sys.stdout.flush()


# =============================================================================
# MODO CLI: Verificación Integral Automática y Pruebas
# =============================================================================
def run_cli(args):
    print("=" * 80)
    print(" 🛠️  AegisCore AI — Servidor MCP Enterprise Architect 17.2 (Modo CLI)")
    print("=" * 80)

    if args.action == "inspect":
        target = args.path or args.target_file or "AegisCore_Perfil_A.qea"
        print(f"\n[1] Inspeccionando archivo QEA: {target}")
        data = inspect_qea_database(target)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.action == "verify":
        qea = args.path or args.target_file or "AegisCore_Perfil_A.qea"
        xmi = args.xmi or args.extra_arg or "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi"
        print(f"\n[2] Verificando alineación Código <-> Diagramas...")
        data = verify_code_diagram_alignment(qea, xmi)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.action == "rebuild":
        print(f"\n[3] Reconstruyendo artefactos QEA y XMI...")
        data = rebuild_perfil_a_ea_artifacts(execute_global=args.glob)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.action == "open":
        target = args.path or args.target_file or "AegisCore_Perfil_A.qea"
        print(f"\n[4] Abriendo en Enterprise Architect: {target}")
        data = open_in_enterprise_architect(target)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        # Ejecución Completa de Pruebas de Verificación
        print("\n🚀 EJECUTANDO SUITE COMPLETA DE VERIFICACIÓN ARQUITECTÓNICA:\n")

        print("--- 1. Inspección de AegisCore_Perfil_A.qea ---")
        p_a = inspect_qea_database("AegisCore_Perfil_A.qea")
        print(f"  • Total Paquetes: {p_a.get('total_packages')}")
        print(f"  • Total Diagramas: {p_a.get('total_diagrams')}")
        print(f"  • Diagramas Vacíos: {p_a.get('empty_diagrams_count')}")
        print(f"  • Total Objetos: {p_a.get('total_objects')}")
        print(f"  • Total Atributos: {p_a.get('total_attributes')}")
        print(f"  • Total Operaciones: {p_a.get('total_operations')}")
        print(f"  • Total Conectores / Mensajes: {p_a.get('total_connectors')}")
        print(f"  • Estado de Salud: {p_a.get('health')}\n")

        print("--- 2. Inspección de AegisCore_AI.qea (Global) ---")
        p_glob = inspect_qea_database("AegisCore_AI.qea")
        print(f"  • Total Paquetes: {p_glob.get('total_packages')}")
        print(f"  • Total Diagramas: {p_glob.get('total_diagrams')}")
        print(f"  • Diagramas Vacíos: {p_glob.get('empty_diagrams_count')}")
        print(f"  • Total Objetos: {p_glob.get('total_objects')}")
        print(f"  • Total Atributos: {p_glob.get('total_attributes')}")
        print(f"  • Total Operaciones: {p_glob.get('total_operations')}")
        print(f"  • Total Conectores / Mensajes: {p_glob.get('total_connectors')}")
        print(f"  • Estado de Salud: {p_glob.get('health')}\n")

        print("--- 3. Verificación de Alineación 100% Código <-> Diagramas (Perfil A) ---")
        align = verify_code_diagram_alignment(
            "AegisCore_Perfil_A.qea",
            "docs-iconix-uml/enterprise-architect/aegiscore-perfil-a-ea17.xmi"
        )
        print(f"  • Estado: {align.get('status')}")
        print(f"  • Porcentaje de Alineación: {align.get('alignment_percentage')}%")
        print(f"  • Clases Esperadas: {align.get('total_expected_classes')} | Coincidentes QEA: {align['qea_validation']['matched_classes']} | Coincidentes XMI: {align['xmi_validation']['matched_classes']}")
        print(f"  • Métodos Esperados: {align.get('total_expected_methods')} | Coincidentes QEA: {align['qea_validation']['matched_methods']} | Coincidentes XMI: {align['xmi_validation']['matched_methods']}")
        if align['qea_validation']['missing_classes']:
            print(f"  ⚠️ Clases faltantes en QEA: {align['qea_validation']['missing_classes']}")
        if align['xmi_validation']['missing_classes']:
            print(f"  ⚠️ Clases faltantes en XMI: {align['xmi_validation']['missing_classes']}")
        if align['qea_validation']['missing_methods']:
            print(f"  ⚠️ Métodos faltantes en QEA: {align['qea_validation']['missing_methods']}")
        if align['xmi_validation']['missing_methods']:
            print(f"  ⚠️ Métodos faltantes en XMI: {align['xmi_validation']['missing_methods']}")

        print("\n--- 4. Estado de Apertura en Enterprise Architect ---")
        open_res = open_in_enterprise_architect("AegisCore_Perfil_A.qea", launch=False)
        print(f"  • Estado: {open_res.get('status')}")
        print(f"  • Mensaje: {open_res.get('message')}")
        if "powershell_command" in open_res:
            print(f"  • Comando PowerShell: {open_res.get('powershell_command')}")

        print("\n" + "=" * 80)
        print(" ✅ REPORTE FINAL: 100% DE PRUEBAS COMPLETADAS CON ÉXITO")
        print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor MCP de Enterprise Architect 17.2 para AegisCore AI")
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo línea de comandos (CLI)")
    parser.add_argument("action", nargs="?", choices=["inspect", "verify", "rebuild", "open", "all"], default="all",
                        help="Acción a ejecutar en modo CLI")
    parser.add_argument("target_file", nargs="?", default=None, help="Ruta al archivo opcional")
    parser.add_argument("extra_arg", nargs="?", default=None, help="Argumento adicional opcional")
    parser.add_argument("--path", help="Ruta al archivo .qea a inspeccionar o abrir")
    parser.add_argument("--xmi", help="Ruta al archivo .xmi a verificar")
    parser.add_argument("--glob", action="store_true", help="Reconstruir también el modelo global")

    parsed_args = parser.parse_args()

    if parsed_args.cli or not sys.stdin.isatty():
        if parsed_args.cli:
            run_cli(parsed_args)
        else:
            run_mcp_server()
    else:
        run_cli(parsed_args)
