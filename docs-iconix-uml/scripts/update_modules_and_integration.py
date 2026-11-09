import sqlite3
import uuid

def generate_guid():
    return "{" + str(uuid.uuid4()).upper() + "}"

def main():
    db_path = "AegisCore_AI.qea"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    print("=== Actualizando AegisCore_AI.qea para Secciones 4.4 y 4.5 ===")

    # 1. Asegurar connector para CU03 con Actor 14 (Director Comercial y Finanzas) si no existe
    c.execute("SELECT Connector_ID FROM t_connector WHERE Start_Object_ID = 14 AND End_Object_ID = 23")
    row = c.fetchone()
    if not row:
        c.execute("""
            INSERT INTO t_connector (Connector_Type, Start_Object_ID, End_Object_ID, Name, Direction, SourceCard, DestCard, ea_guid)
            VALUES ('Use Case', 14, 23, 'Administra Catálogo de Planes', 'Unspecified', '', '', ?)
        """, (generate_guid(),))
        conn.commit()
        print("  -> Creado conector Actor 14 -> CU03")

    # Obtener IDs de conectores de Casos de Uso
    c.execute("SELECT Connector_ID, Start_Object_ID, End_Object_ID FROM t_connector WHERE Connector_Type = 'Use Case'")
    uc_connectors = c.fetchall()
    print(f"  -> Conectores Use Case disponibles: {len(uc_connectors)}")

    # 2. Reorganizar Diagrama 2 (01. Diagrama General de Casos de Uso del Sistema CU01-CU15) sin traslapes
    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 2")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 2")

    # Actores a la izquierda (10, 11, 12, 13) y derecha (14, 15, 16)
    actors_layout = [
        (10, 40, -80, 160, -160),    # Cliente Asegurado
        (11, 40, -220, 160, -300),   # Perito de Campo
        (12, 40, -360, 160, -440),   # Ajustador de Siniestros
        (13, 40, -500, 160, -580),   # Auditor de Riesgos BI
        (14, 1340, -100, 1460, -180), # Director Comercial Finanzas
        (15, 1340, -260, 1460, -340), # Broker Apache Kafka
        (16, 1340, -420, 1460, -500), # Bot WhatsApp y Servidor MCP
    ]
    for obj_id, l, t, r, b in actors_layout:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (2, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    # Casos de Uso en 3 columnas limpias
    # Columna 1: Módulo Comercial (21, 22, 23, 24, 25)
    # Columna 2: Módulo Siniestros (26, 27, 28, 29, 30)
    # Columna 3: Módulo IA & MCP (31, 32, 33, 34, 35)
    cols_uc = [
        # (Obj_ID, Col_Left, Top, Col_Right, Bottom)
        # Columna 1: X 260 a 560
        (21, 260, -60, 560, -125),
        (22, 260, -150, 560, -215),
        (23, 260, -240, 560, -305),
        (24, 260, -330, 560, -395),
        (25, 260, -420, 560, -485),
        # Columna 2: X 620 a 920
        (26, 620, -60, 920, -125),
        (27, 620, -150, 920, -215),
        (28, 620, -240, 920, -305),
        (29, 620, -330, 920, -395),
        (30, 620, -420, 920, -485),
        # Columna 3: X 980 a 1280
        (31, 980, -60, 1280, -125),
        (32, 980, -150, 1280, -215),
        (33, 980, -240, 1280, -305),
        (34, 980, -330, 1280, -395),
        (35, 980, -420, 1280, -485),
    ]
    for obj_id, l, t, r, b in cols_uc:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (2, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    # Links en Diagrama 2
    for conn_id, s_id, e_id in uc_connectors:
        c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (2, ?, 0)", (conn_id,))

    print("  -> Diagrama 2 reorganizado en 3 columnas sin traslapes.")

    # 3. Poblar Diagrama 3: 4.4.1. Módulo Comercial y SSO (CU01-CU05)
    c.execute("UPDATE t_diagram SET Name = '4.4.1. Módulo Comercial y SSO (CU01 al CU05)' WHERE Diagram_ID = 3")
    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 3")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 3")

    # Actores: Cliente (10), Director Comercial (14), Bot WhatsApp / n8n (16)
    d3_actors = [
        (10, 40, -120, 160, -200),
        (14, 40, -280, 160, -360),
        (16, 820, -320, 940, -400),
    ]
    for obj_id, l, t, r, b in d3_actors:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (3, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    d3_ucs = [
        (21, 280, -50, 680, -115),   # CU01 SSO
        (22, 280, -140, 680, -205),  # CU02 GraphQL
        (23, 280, -230, 680, -295),  # CU03 Planes
        (24, 280, -320, 680, -385),  # CU04 Cotización IA Local
        (25, 280, -410, 680, -475),  # CU05 WhatsApp Factura n8n
    ]
    for obj_id, l, t, r, b in d3_ucs:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (3, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    # Links para D3
    c.execute("SELECT Connector_ID FROM t_connector WHERE End_Object_ID IN (21, 22, 23, 24, 25)")
    for (cid,) in c.fetchall():
        c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (3, ?, 0)", (cid,))
    print("  -> Diagrama 3 poblado con 3 actores, 5 CUs y sus conectores.")

    # 4. Poblar Diagrama 4: 4.4.2. Módulo Siniestros, Móvil y Saga (CU06-CU10)
    c.execute("UPDATE t_diagram SET Name = '4.4.2. Módulo Siniestros, Móvil y Saga (CU06 al CU10)' WHERE Diagram_ID = 4")
    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 4")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 4")

    # Actores: Cliente (10), Perito (11), Ajustador (12), Kafka (15)
    d4_actors = [
        (10, 40, -80, 160, -160),
        (11, 40, -240, 160, -320),
        (12, 820, -160, 940, -240),
        (15, 820, -320, 940, -400),
    ]
    for obj_id, l, t, r, b in d4_actors:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (4, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    d4_ucs = [
        (26, 280, -50, 680, -115),   # CU06 SOS Triaje
        (27, 280, -140, 680, -205),  # CU07 Inspección TFLite
        (28, 280, -230, 680, -295),  # CU08 Sync DynamoDB
        (29, 280, -320, 680, -385),  # CU09 Saga Transversal Kafka
        (30, 280, -410, 680, -475),  # CU10 Pago QR Idempotente
    ]
    for obj_id, l, t, r, b in d4_ucs:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (4, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    # Links para D4
    c.execute("SELECT Connector_ID FROM t_connector WHERE End_Object_ID IN (26, 27, 28, 29, 30)")
    for (cid,) in c.fetchall():
        c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (4, ?, 0)", (cid,))
    print("  -> Diagrama 4 poblado con 4 actores, 5 CUs y sus conectores.")

    # 5. Poblar Diagrama 5: 4.4.3. Módulo Inteligencia Artificial y Servidor MCP (CU11-CU15)
    c.execute("UPDATE t_diagram SET Name = '4.4.3. Módulo Inteligencia Artificial y Servidor MCP (CU11 al CU15)' WHERE Diagram_ID = 5")
    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 5")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 5")

    # Actores: Ajustador (12), Auditor BI (13), Director (14), Bot MCP (16)
    d5_actors = [
        (12, 40, -80, 160, -160),
        (13, 40, -240, 160, -320),
        (14, 820, -160, 940, -240),
        (16, 820, -320, 940, -400),
    ]
    for obj_id, l, t, r, b in d5_actors:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (5, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    d5_ucs = [
        (31, 280, -50, 680, -115),   # CU11 CNN CrashNet
        (32, 280, -140, 680, -205),  # CU12 Random Forest
        (33, 280, -230, 680, -295),  # CU13 K-Means & Fraud
        (34, 280, -320, 680, -385),  # CU14 LangGraph Metas
        (35, 280, -410, 680, -475),  # CU15 Voz MCP Anti-SQLi
    ]
    for obj_id, l, t, r, b in d5_ucs:
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (5, ?, ?, ?, ?, ?, 1)",
                  (obj_id, l, t, r, b))

    # Links para D5
    c.execute("SELECT Connector_ID FROM t_connector WHERE End_Object_ID IN (31, 32, 33, 34, 35)")
    for (cid,) in c.fetchall():
        c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (5, ?, 0)", (cid,))
    print("  -> Diagrama 5 poblado con 4 actores, 5 CUs y sus conectores.")

    # 6. Actualizar nombres de diagramas de secuencia para reflejar secciones 4.4 y 4.5
    rename_seq = [
        (19, "4.4.1. Secuencia UML 2.5+ - CU01 (Autenticación SSO Keycloak)"),
        (20, "4.4.1. Secuencia UML 2.5+ - CU05 (Flujo WhatsApp a Factura n8n)"),
        (21, "4.4.2. Secuencia UML 2.5+ - CU06 (Triaje SOS Geoespacial)"),
        (22, "4.4.2. Secuencia UML 2.5+ - CU07 (Inspección Offline TFLite)"),
        (23, "4.4.2. Secuencia UML 2.5+ - CU08 (Sync Idempotente DynamoDB)"),
        (24, "4.5.1. Secuencia UML 2.5+ - CU09 (Saga Transversal y Rollback Kafka)"),
        (25, "4.4.2. Secuencia UML 2.5+ - CU10 (Pago QR Idempotente)"),
        (26, "4.4.3. Secuencia UML 2.5+ - CU11 (Detección Choques CrashNet)"),
        (27, "4.4.3. Secuencia UML 2.5+ - CU14 (Agente Autónomo LangGraph)"),
        (28, "4.4.3. Secuencia UML 2.5+ - CU15 (Voz MCP con Filtro Anti-SQLi)"),
        (30, "4.5.2. Diagrama de Componentes y Arquitectura Global en 4 Niveles"),
    ]
    for did, new_name in rename_seq:
        c.execute("UPDATE t_diagram SET Name = ? WHERE Diagram_ID = ?", (new_name, did))
    print("  -> Renombrados diagramas de secuencia y componentes con nomenclatura 4.4 y 4.5.")

    # 7. Crear Diagrama 34: "4.4. Desarrollo de los Módulos del Sistema" en Package 2 (Raíz)
    c.execute("SELECT Diagram_ID FROM t_diagram WHERE Diagram_ID = 34")
    if not c.fetchone():
        c.execute("""
            INSERT INTO t_diagram (Diagram_ID, Package_ID, ParentID, Diagram_Type, Name, Version, Author, ShowDetails, Notes, Orientation, cx, cy, Scale, CreatedDate, ModifiedDate, ShowForeign, ShowBorder, ShowPackageContents, Locked, ea_guid)
            VALUES (34, 2, 0, 'Custom', '4.4. Desarrollo de los Módulos del Sistema', '1.0', 'AegisCore Architecture Team', 0, 'Vista global ejecutiva de los 3 módulos del sistema y trazabilidad de los 15 Casos de Uso ICONIX.', 'L', 1600, 900, 100, datetime('now'), datetime('now'), 1, 1, 1, 0, ?)
        """, (generate_guid(),))
        print("  -> Creado Diagrama 34 (4.4. Desarrollo de los Módulos del Sistema)")
    else:
        c.execute("UPDATE t_diagram SET Name = '4.4. Desarrollo de los Módulos del Sistema', Package_ID = 2 WHERE Diagram_ID = 34")

    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 34")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 34")

    # Colocar los 3 paquetes de módulos y sus relaciones en Diagrama 34
    # Package 3: X: 60, Y: -100, W: 380, H: 450
    # Package 4: X: 520, Y: -100, W: 380, H: 450
    # Package 5: X: 980, Y: -100, W: 380, H: 450
    c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (34, 3, 60, -100, 440, -550, 1)")
    c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (34, 4, 520, -100, 900, -550, 2)")
    c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (34, 5, 980, -100, 1360, -550, 3)")

    # Conectores entre paquetes (1, 2)
    c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (34, 1, 0)")
    c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Hidden) VALUES (34, 2, 0)")

    # 8. Crear Diagrama 35: "4.5. Integración de Componentes" en Package 2 (Raíz)
    c.execute("SELECT Diagram_ID FROM t_diagram WHERE Diagram_ID = 35")
    if not c.fetchone():
        c.execute("""
            INSERT INTO t_diagram (Diagram_ID, Package_ID, ParentID, Diagram_Type, Name, Version, Author, ShowDetails, Notes, Orientation, cx, cy, Scale, CreatedDate, ModifiedDate, ShowForeign, ShowBorder, ShowPackageContents, Locked, ea_guid)
            VALUES (35, 2, 0, 'Component', '4.5. Integración de Componentes', '1.0', 'AegisCore Architecture Team', 0, 'Topología de integración transversal entre frontends, API gateways, microservicios, broker Kafka, DynamoDB y bases relacionales/documentales.', 'L', 1800, 1000, 100, datetime('now'), datetime('now'), 1, 1, 1, 0, ?)
        """, (generate_guid(),))
        print("  -> Creado Diagrama 35 (4.5. Integración de Componentes)")
    else:
        c.execute("UPDATE t_diagram SET Name = '4.5. Integración de Componentes', Package_ID = 2 WHERE Diagram_ID = 35")

    c.execute("DELETE FROM t_diagramobjects WHERE Diagram_ID = 35")
    c.execute("DELETE FROM t_diagramlinks WHERE DiagramID = 35")

    # Copiar exactamente los 18 componentes perfectamente diagramados de Diagrama 30 a Diagrama 35
    c.execute("SELECT Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence FROM t_diagramobjects WHERE Diagram_ID = 30")
    for r in c.fetchall():
        c.execute("INSERT INTO t_diagramobjects (Diagram_ID, Object_ID, RectLeft, RectTop, RectRight, RectBottom, Sequence) VALUES (35, ?, ?, ?, ?, ?, ?)", r)

    c.execute("SELECT ConnectorID, Geometry, Style, Hidden, Path FROM t_diagramlinks WHERE DiagramID = 30")
    for r in c.fetchall():
        c.execute("INSERT INTO t_diagramlinks (DiagramID, ConnectorID, Geometry, Style, Hidden, Path) VALUES (35, ?, ?, ?, ?, ?)", r)

    conn.commit()
    conn.close()
    print("=== AegisCore_AI.qea actualizado con éxito total ===")

if __name__ == "__main__":
    main()

