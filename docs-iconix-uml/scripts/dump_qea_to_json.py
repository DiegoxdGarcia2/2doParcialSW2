# -*- coding: utf-8 -*-
import sqlite3
import json

tables = ['t_package', 't_object', 't_operation', 't_diagram', 't_diagramobjects', 't_connector', 't_diagramlinks', 't_attribute']

conn = sqlite3.connect('AegisCore_AI.qea')
cur = conn.cursor()

data = {}
for tbl in tables:
    cur.execute(f"PRAGMA table_info({tbl})")
    cols = [col[1] for col in cur.fetchall()]
    
    cur.execute(f"SELECT * FROM {tbl}")
    rows = cur.fetchall()
    
    data[tbl] = {
        "columns": cols,
        "rows": rows
    }
    print(f"Dumped {tbl}: {len(rows)} rows, {len(cols)} columns")

conn.close()

with open('ea_data_dump.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)

print("Exportado ea_data_dump.json con éxito.")

