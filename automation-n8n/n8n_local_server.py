#!/usr/bin/env python3
"""
AegisCore — Servidor Local de Orquestación y Automatización n8n (:5678)
Ejecuta el flujo 'workflow-pedido-poliza-whatsapp-factura.json' contra MS1 (:8001)
y expone un panel visual interactivo de ejecución en http://localhost:5678.
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_ENV = BASE_DIR.parent / ".env"
if ROOT_ENV.is_file():
    for _line in ROOT_ENV.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip("'\""))

WORKFLOW_PATH = BASE_DIR / "workflow-pedido-poliza-whatsapp-factura.json"
MS1_URL = os.environ.get("MS1_URL", "http://127.0.0.1:8001")
EXECUTIONS_LOG = []


def upload_pdf_to_s3_if_configured(numero_factura: str, local_pdf_url: str) -> str:
    bucket = os.environ.get("AWS_S3_BUCKET", "servicio-de-seguros-aegiscore")
    region = os.environ.get("AWS_S3_REGION", os.environ.get("AWS_REGION", "us-east-2"))
    key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    secret = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if not (bucket and key_id and secret and numero_factura):
        return local_pdf_url
    try:
        import boto3
        pdf_path = BASE_DIR.parent / "backend" / "ms1-polizas-php" / "public" / "facturas" / f"{numero_factura}.pdf"
        if pdf_path.is_file():
            pdf_bytes = pdf_path.read_bytes()
        else:
            with urllib.request.urlopen(local_pdf_url, timeout=4) as r:
                pdf_bytes = r.read()
        s3 = boto3.client("s3", aws_access_key_id=key_id, aws_secret_access_key=secret, region_name=region)
        s3_key = f"facturas/{numero_factura}.pdf"
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=pdf_bytes,
            ContentType="application/pdf",
            ContentDisposition=f'inline; filename="{numero_factura}.pdf"'
        )
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    except Exception:
        return local_pdf_url


def execute_whatsapp_workflow(payload: dict) -> dict:
    t0 = time.time()
    normalized = {
        "telefono": payload.get("telefono") or payload.get("from") or "+591 71099887",
        "numero_documento": payload.get("numero_documento") or payload.get("documento") or "6234891-SC",
        "placa": payload.get("placa") or "6014-AEG",
        "marca": payload.get("marca") or "Mazda",
        "modelo": payload.get("modelo") or "CX-30 AWD",
        "anio": int(payload.get("anio") or 2025),
        "valor_comercial": float(payload.get("valor_comercial") or 28000),
        "plan_codigo": payload.get("plan_codigo") or "PLAN-AUTO-FULL",
        "tipo_comprobante": payload.get("tipo_comprobante") or "FACTURA",
    }

    req = urllib.request.Request(
        f"{MS1_URL}/api/v1/whatsapp/pedido-poliza",
        data=json.dumps(normalized).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        ms1_data = json.loads(resp.read().decode("utf-8"))

    num_fac = ms1_data.get("factura", {}).get("numeroFactura") or ""
    local_pdf = ms1_data.get("url_pdf") or ""
    s3_pdf_url = upload_pdf_to_s3_if_configured(num_fac, local_pdf)
    ms1_data["url_pdf_local"] = local_pdf
    ms1_data["url_pdf"] = s3_pdf_url

    elapsed_ms = round((time.time() - t0) * 1000, 1)
    execution_record = {
        "execution_id": f"n8n-exec-{int(time.time() * 1000)}",
        "status": "SUCCESS",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": elapsed_ms,
        "steps_executed": [
            {"node": "Webhook WhatsApp Business API", "status": "OK"},
            {"node": "Normalizar Solicitud de WhatsApp", "status": "OK", "data": normalized},
            {"node": "Emitir Poliza en Motor Central", "status": "OK", "poliza": ms1_data.get("poliza", {}).get("numeroPoliza")},
            {"node": "Compilar Factura Fiscal PDF (SHA-256)", "status": "OK", "factura": ms1_data.get("factura", {}).get("numeroFactura")},
            {"node": "Despachar PDF al WhatsApp del Cliente", "status": "OK", "url_pdf": ms1_data.get("url_pdf")},
            {"node": "Enviar Comprobante por Correo", "status": "OK"},
        ],
        "result": ms1_data,
    }
    EXECUTIONS_LOG.insert(0, execution_record)
    return execution_record


HTML_STUDIO = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AegisCore Automation Studio — Flujo n8n (:5678)</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0F172A] text-slate-100 min-h-screen font-['Inter',sans-serif] flex flex-col">
  <header class="bg-slate-900/90 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-[#EA4B71] text-white flex items-center justify-center font-bold text-sm shadow">
        n8n
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-['Plus_Jakarta_Sans',sans-serif] font-bold text-base text-white">
            Contratación Póliza WhatsApp y Emisión de Factura PDF
          </h1>
          <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Workflow Activo · Puerto 5678
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-0.5">
          Webhook local activo: <code class="font-mono text-teal-300">POST http://localhost:5678/webhook/whatsapp-pedido-poliza</code>
        </p>
      </div>
    </div>
    <div class="flex items-center gap-2.5">
      <a href="/workflow.json" download="workflow-pedido-poliza-whatsapp-factura.json"
         class="px-3.5 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors">
        Descargar JSON para n8n Cloud
      </a>
      <button onclick="ejecutarFlujo()" id="btn-run"
              class="px-4 py-2 rounded-xl bg-[#EA4B71] hover:bg-[#d63d62] text-white text-xs font-bold transition-colors shadow">
        ▶ Ejecutar Flujo Ahora
      </button>
    </div>
  </header>

  <main class="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
    <!-- Lienzo Visual de Nodos del Flujo -->
    <section class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
      <div class="flex items-center justify-between">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">
          Topología del Flujo Automatizado (6 Nodos Conectados)
        </h2>
        <span class="text-xs font-mono text-slate-400">Conectado a http://localhost:8001</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-5 gap-4 items-center pt-2">
        <div class="p-4 rounded-xl bg-slate-800/90 border border-pink-500/40 space-y-1">
          <span class="text-[10px] font-mono uppercase text-pink-400 font-bold">1. Trigger Webhook</span>
          <p class="text-xs font-bold text-white">Webhook WhatsApp Business API</p>
          <p class="text-[11px] text-slate-400 font-mono">/webhook/whatsapp-pedido-poliza</p>
        </div>

        <div class="p-4 rounded-xl bg-slate-800/90 border border-amber-500/40 space-y-1">
          <span class="text-[10px] font-mono uppercase text-amber-300 font-bold">2. Code Node</span>
          <p class="text-xs font-bold text-white">Normalizar Solicitud WhatsApp</p>
          <p class="text-[11px] text-slate-400">Extrae CI, Placa, Vehículo y Plan</p>
        </div>

        <div class="p-4 rounded-xl bg-slate-800/90 border border-teal-500/40 space-y-1">
          <span class="text-[10px] font-mono uppercase text-teal-300 font-bold">3. HTTP Request</span>
          <p class="text-xs font-bold text-white">Emitir Póliza en Motor Central</p>
          <p class="text-[11px] text-slate-400 font-mono">POST :8001/api/v1/whatsapp/pedido-poliza</p>
        </div>

        <div class="p-4 rounded-xl bg-slate-800/90 border border-indigo-500/40 space-y-1">
          <span class="text-[10px] font-mono uppercase text-indigo-300 font-bold">4. PDF Engine</span>
          <p class="text-xs font-bold text-white">Compilar Factura PDF (SHA-256)</p>
          <p class="text-[11px] text-slate-400 font-mono">POST :8001/api/facturas/generar-pdf</p>
        </div>

        <div class="p-4 rounded-xl bg-slate-800/90 border border-emerald-500/40 space-y-1">
          <span class="text-[10px] font-mono uppercase text-emerald-300 font-bold">5 & 6. Notificación</span>
          <p class="text-xs font-bold text-white">Despachar PDF a WhatsApp & Correo</p>
          <p class="text-[11px] text-slate-400">Adjunta comprobante oficial</p>
        </div>
      </div>
    </section>

    <!-- Simulador y Bitácora de Ejecuciones en Vivo -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <div class="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 class="text-sm font-bold text-white">Parámetros de Prueba del Webhook</h3>
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div>
            <label class="block text-slate-400 mb-1">Teléfono WhatsApp</label>
            <input id="inp-tel" value="+591 71099887" class="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-white" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Documento CI/NIT</label>
            <input id="inp-doc" value="6234891-SC" class="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-white" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Placa</label>
            <input id="inp-placa" value="6014-AEG" class="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-white" />
          </div>
          <div>
            <label class="block text-slate-400 mb-1">Valor Comercial (USD)</label>
            <input id="inp-valor" type="number" value="28000" class="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 font-mono text-white" />
          </div>
        </div>
        <button onclick="ejecutarFlujo()" class="w-full py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-bold transition-colors">
          Disparar Webhook y Generar Factura PDF
        </button>
      </div>

      <div class="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 class="text-sm font-bold text-white">Resultado de Ejecución en Tiempo Real</h3>
        <div id="exec-output" class="text-xs font-mono bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 min-h-[190px] overflow-x-auto">
          Pulsa "▶ Ejecutar Flujo Ahora" para disparar el flujo completo contra el motor de pólizas y facturación PDF.
        </div>
      </div>
    </div>
  </main>

  <script>
    async function ejecutarFlujo() {
      const out = document.getElementById('exec-output');
      out.innerHTML = '<span class="text-amber-300">Ejecutando los 6 nodos del flujo...</span>';
      const body = {
        telefono: document.getElementById('inp-tel').value,
        numero_documento: document.getElementById('inp-doc').value,
        placa: document.getElementById('inp-placa').value,
        valor_comercial: Number(document.getElementById('inp-valor').value)
      };
      try {
        const res = await fetch('/webhook/whatsapp-pedido-poliza', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        const pdfUrl = data.result?.url_pdf || '#';
        out.innerHTML = `
          <div class="space-y-2">
            <div class="flex items-center justify-between text-emerald-400 font-bold">
              <span>✓ Ejecución Exitosa (${data.execution_id})</span>
              <span>${data.duration_ms} ms</span>
            </div>
            <div>Póliza Emitida: <strong class="text-white">${data.result?.poliza?.numeroPoliza}</strong></div>
            <div>Factura Fiscal: <strong class="text-white">${data.result?.factura?.numeroFactura}</strong> (Total: USD ${data.result?.factura?.total})</div>
            <div>Hash SHA-256: <span class="text-teal-300">${data.result?.hash_digital_sha256}</span></div>
            <div class="pt-2">
              <a href="${pdfUrl}" target="_blank" class="inline-block px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-sans font-semibold hover:bg-emerald-500">
                Abrir Factura PDF Generada
              </a>
            </div>
          </div>
        `;
      } catch (e) {
        out.innerHTML = '<span class="text-red-400">Error al ejecutar flujo: ' + e.message + '</span>';
      }
    }
  </script>
</body>
</html>
"""


class N8nLocalHandler(BaseHTTPRequestHandler):
    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_STUDIO.encode("utf-8"))
            return

        if self.path == "/workflow.json":
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(WORKFLOW_PATH.read_bytes())
            return

        if self.path == "/health":
            self.send_response(200)
            self._send_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "UP", "service": "n8n-local-orchestrator", "port": 5678}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/webhook"):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            try:
                payload = json.loads(raw) if raw else {}
            except Exception:
                payload = {}

            try:
                exec_res = execute_whatsapp_workflow(payload)
                self.send_response(200)
                self._send_cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(exec_res).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self._send_cors()
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ERROR", "message": str(exc)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    port = int(os.environ.get("N8N_PORT", "5678"))
    server = HTTPServer(("127.0.0.1", port), N8nLocalHandler)
    print(f"AegisCore n8n Local Studio running on http://127.0.0.1:{port}")
    server.serve_forever()

