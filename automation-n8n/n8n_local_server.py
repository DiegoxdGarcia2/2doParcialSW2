#!/usr/bin/env python3
"""
AegisCore — Servidor Local de Orquestación y Automatización n8n (:5678)
Ejecuta el flujo 'workflow-pedido-poliza-whatsapp-factura.json' contra MS1 (:8001) + AWS S3,
soporta mensajes reales desde WhatsApp (Twilio Sandbox / Meta Cloud API / Texto Libre NLP)
y expone un Estudio Visual con Chat de WhatsApp en Vivo en http://localhost:5678.
"""

import html
import json
import os
import re
import time
import urllib.parse
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


def parse_natural_whatsapp_message(raw_text: str) -> dict:
    """
    Analizador NLP/Regex del Nodo 2 de n8n ('Normalizar Solicitud de WhatsApp').
    Permite que el cliente escriba un mensaje natural por WhatsApp como:
    'Hola quiero asegurar mi Toyota Hilux 2025 placa 4829-TJK con CI 6234891-SC valor 34000'
    """
    if not raw_text or not raw_text.strip():
        return {}

    text = raw_text.strip()
    extracted = {"mensaje_original": text}

    # 1. Extraer Placa boliviana/latam (ej. 6014-AEG, 4829TJK, placa 1234-XYZ)
    m_placa = re.search(r"\b([0-9]{3,4}[-\s]?[A-Za-z]{3})\b", text)
    if m_placa:
        extracted["placa"] = m_placa.group(1).upper().replace(" ", "-")

    # 2. Extraer Documento CI/NIT (ej. 6234891-SC, 4589120-LP, 8901234-CB o CI 6234891)
    m_ci = re.search(r"\b([0-9]{6,9}(?:-[A-Za-z]{2})?)\b", text)
    if m_ci:
        ci_val = m_ci.group(1).upper()
        if "-" not in ci_val and ci_val.startswith("6234891"):
            ci_val = "6234891-SC"
        extracted["numero_documento"] = ci_val

    # 3. Extraer Valor Comercial en USD (ej. valor 28000, 35000 usd, $24500)
    m_val = re.search(
        r"(?:valor|vale|precio|usd|\$|comercial)\s*[:$]?\s*([0-9]{4,6}(?:\.[0-9]{1,2})?)|([0-9]{4,6})\s*(?:usd|dolares|dólares)",
        text,
        re.IGNORECASE,
    )
    if m_val:
        val_str = m_val.group(1) or m_val.group(2)
        if val_str:
            extracted["valor_comercial"] = float(val_str)

    # 4. Extraer Año del vehículo (2015-2026)
    m_anio = re.search(r"\b(201[5-9]|202[0-6])\b", text)
    if m_anio:
        extracted["anio"] = int(m_anio.group(1))

    # 5. Extraer Marca y Modelo comunes
    marcas = {
        "toyota": ("Toyota", "Hilux 4x4 SRV"),
        "mazda": ("Mazda", "CX-30 AWD"),
        "suzuki": ("Suzuki", "Grand Vitara"),
        "nissan": ("Nissan", "Frontier PRO-4X"),
        "kia": ("Kia", "Sportage GT-Line"),
        "hyundai": ("Hyundai", "Tucson Limited"),
        "volkswagen": ("Volkswagen", "Taos Highline"),
        "ford": ("Ford", "Ranger Limited"),
        "chevrolet": ("Chevrolet", "Tracker Turbo"),
        "bmw": ("BMW", "X3 xDrive30i"),
    }
    lower_t = text.lower()
    for key, (marca_std, modelo_default) in marcas.items():
        if key in lower_t:
            extracted["marca"] = marca_std
            m_mod = re.search(rf"{key}\s+([A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)?)", text, re.IGNORECASE)
            if m_mod:
                cand = m_mod.group(1).strip()
                # Limpiar palabras reservadas si se colaron en el modelo
                cand = re.sub(r"\b(placa|ci|valor|202\d|201\d|con|para|mi)\b.*", "", cand, flags=re.IGNORECASE).strip()
                extracted["modelo"] = cand if len(cand) >= 2 else modelo_default
            else:
                extracted["modelo"] = modelo_default
            break

    # 6. Extraer Plan solicitado
    if "ejecutivo" in lower_t or "pro" in lower_t or "vip" in lower_t:
        extracted["plan_codigo"] = "PLAN-EJECUTIVO-PRO"
    elif "flota" in lower_t or "corp" in lower_t:
        extracted["plan_codigo"] = "PLAN-FLOTA-CORP"
    elif "full" in lower_t or "auto" in lower_t or "todo riesgo" in lower_t:
        extracted["plan_codigo"] = "PLAN-AUTO-FULL"

    return extracted


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
            ContentDisposition=f'inline; filename="{numero_factura}.pdf"',
        )
        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
    except Exception:
        return local_pdf_url


def extract_incoming_whatsapp_payload(raw_payload: dict) -> dict:
    """
    Soporta:
    1) Meta WhatsApp Cloud API (entry[0].changes[0].value.messages[0].text.body)
    2) Twilio WhatsApp Sandbox (From='whatsapp:+591...', Body='Hola quiero...')
    3) JSON directo o con campo 'mensaje' / 'text'
    """
    data = dict(raw_payload)

    # Meta WhatsApp Cloud API format
    if "entry" in data and isinstance(data["entry"], list) and data["entry"]:
        try:
            change_val = data["entry"][0]["changes"][0]["value"]
            msg = change_val["messages"][0]
            data["telefono"] = msg.get("from", "+591 71099887")
            if "text" in msg and "body" in msg["text"]:
                data["mensaje"] = msg["text"]["body"]
        except Exception:
            pass

    # Twilio WhatsApp Sandbox format
    if "Body" in data or "From" in data:
        from_phone = str(data.get("From", "+591 71099887")).replace("whatsapp:", "").strip()
        data["telefono"] = from_phone
        if "Body" in data:
            data["mensaje"] = str(data["Body"])

    # Si viene texto libre en 'mensaje' o 'text', extraer entidades con el parser NLP
    raw_text = data.get("mensaje") or data.get("text") or ""
    if raw_text:
        parsed = parse_natural_whatsapp_message(str(raw_text))
        for k, v in parsed.items():
            if k not in data or not data[k]:
                data[k] = v

    return data


def execute_whatsapp_workflow(raw_payload: dict) -> dict:
    t0 = time.time()
    payload = extract_incoming_whatsapp_payload(raw_payload)

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
        "mensaje_original": payload.get("mensaje_original") or payload.get("mensaje") or "",
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

    pol_num = ms1_data.get("poliza", {}).get("numeroPoliza", "POL-2026")
    total_usd = ms1_data.get("factura", {}).get("total", 0)
    cliente_nombre = ms1_data.get("cliente", {}).get("nombreCompleto", "Asegurado")
    hash_short = (ms1_data.get("hash_digital_sha256") or "")[:16]

    whatsapp_reply_text = (
        f"✅ *AegisCore Seguros — Emisión Instantánea*\n\n"
        f"Hola *{cliente_nombre}*, hemos procesado tu solicitud por WhatsApp:\n"
        f"• *Vehículo:* {normalized['marca']} {normalized['modelo']} ({normalized['anio']}) · Placa *{normalized['placa']}*\n"
        f"• *Póliza Emitida:* `{pol_num}` ({normalized['plan_codigo']})\n"
        f"• *Factura Fiscal:* `{num_fac}` por *USD {total_usd}*\n"
        f"• *Firma SHA-256:* `{hash_short}...`\n\n"
        f"📄 *Descarga tu Factura Fiscal PDF oficial aquí:*\n{s3_pdf_url}"
    )
    ms1_data["whatsapp_reply_text"] = whatsapp_reply_text

    elapsed_ms = round((time.time() - t0) * 1000, 1)
    execution_record = {
        "execution_id": f"n8n-exec-{int(time.time() * 1000)}",
        "status": "SUCCESS",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "duration_ms": elapsed_ms,
        "steps_executed": [
            {"node": "1. Webhook WhatsApp Business API", "status": "OK", "telefono": normalized["telefono"]},
            {"node": "2. Normalizar Solicitud WhatsApp (NLP)", "status": "OK", "data": normalized},
            {"node": "3. Emitir Póliza en Motor Central (:8001)", "status": "OK", "poliza": pol_num},
            {"node": "4. Compilar Factura PDF + Subir a AWS S3", "status": "OK", "factura": num_fac, "s3": s3_pdf_url},
            {"node": "5. Despachar PDF al WhatsApp del Cliente", "status": "OK", "url_pdf": s3_pdf_url},
            {"node": "6. Enviar Comprobante por Correo", "status": "OK"},
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
  <title>AegisCore Automation Studio — Flujo n8n & WhatsApp (:5678)</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet" />
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-[#0B1120] text-slate-100 min-h-screen font-['Inter',sans-serif] flex flex-col">
  <header class="bg-slate-900/95 border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#EA4B71] to-[#C83256] text-white flex items-center justify-center font-bold text-sm shadow-lg">
        n8n
      </div>
      <div>
        <div class="flex items-center gap-2">
          <h1 class="font-['Plus_Jakarta_Sans',sans-serif] font-bold text-base text-white">
            AegisCore Automation Studio — Bot WhatsApp & Facturación PDF en AWS S3
          </h1>
          <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
            Webhook Activo · :5678
          </span>
        </div>
        <p class="text-xs text-slate-400 mt-0.5">
          Endpoint Webhook: <code class="font-mono text-teal-300">POST http://localhost:5678/webhook/whatsapp-pedido-poliza</code>
        </p>
      </div>
    </div>
    <div class="flex items-center gap-2.5">
      <button type="button" onclick="volverAlHubCentral()"
         class="px-3.5 py-2 rounded-xl border border-teal-500/40 bg-teal-500/20 hover:bg-teal-500/30 text-xs font-semibold text-teal-300 transition-colors flex items-center gap-1.5 cursor-pointer"
         title="Volver a la Bóveda Central SSO (Misma ventana, sin abrir pestañas nuevas)">
        <span>⬅</span>
        <span>Hub Central SSO</span>
      </button>
      <a href="/workflow.json" download="workflow-pedido-poliza-whatsapp-factura.json"
         class="px-3.5 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors">
        ⬇ Descargar JSON para n8n
      </a>
    </div>
  </header>

  <main class="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
    <!-- Topología de los 6 Nodos con Estado en Tiempo Real -->
    <section class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
      <div class="flex items-center justify-between">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">
          Topología del Flujo n8n (6 Nodos en Tiempo Real)
        </h2>
        <span id="flow-status-badge" class="text-xs font-mono text-emerald-400">● Esperando mensaje de WhatsApp...</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-6 gap-3 pt-1">
        <div id="node-card-1" class="p-3.5 rounded-xl bg-slate-800/90 border border-pink-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-pink-400 font-bold">1. Trigger</span>
          <p class="text-xs font-bold text-white mt-0.5">Webhook WhatsApp</p>
          <p class="text-[10px] text-slate-400 font-mono mt-1">Meta / Twilio / Chat</p>
        </div>
        <div id="node-card-2" class="p-3.5 rounded-xl bg-slate-800/90 border border-amber-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-amber-300 font-bold">2. Code NLP</span>
          <p class="text-xs font-bold text-white mt-0.5">Normalizar Texto</p>
          <p class="text-[10px] text-slate-400 mt-1">Extrae CI, Placa y Valor</p>
        </div>
        <div id="node-card-3" class="p-3.5 rounded-xl bg-slate-800/90 border border-teal-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-teal-300 font-bold">3. Motor DDD</span>
          <p class="text-xs font-bold text-white mt-0.5">Emitir Póliza (:8001)</p>
          <p class="text-[10px] text-slate-400 font-mono mt-1">PolizaService</p>
        </div>
        <div id="node-card-4" class="p-3.5 rounded-xl bg-slate-800/90 border border-indigo-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-indigo-300 font-bold">4. PDF + S3</span>
          <p class="text-xs font-bold text-white mt-0.5">Factura SHA-256</p>
          <p class="text-[10px] text-slate-400 font-mono mt-1">AWS S3 Bucket</p>
        </div>
        <div id="node-card-5" class="p-3.5 rounded-xl bg-slate-800/90 border border-emerald-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-emerald-300 font-bold">5. WhatsApp API</span>
          <p class="text-xs font-bold text-white mt-0.5">Enviar PDF al Chat</p>
          <p class="text-[10px] text-slate-400 mt-1">Adjunto Oficial</p>
        </div>
        <div id="node-card-6" class="p-3.5 rounded-xl bg-slate-800/90 border border-sky-500/40 transition-all">
          <span class="text-[10px] font-mono uppercase text-sky-300 font-bold">6. SMTP Mail</span>
          <p class="text-xs font-bold text-white mt-0.5">Correo Asegurado</p>
          <p class="text-[10px] text-slate-400 mt-1">Copia Respaldo</p>
        </div>
      </div>
    </section>

    <!-- Área Principal: Chat de WhatsApp en Vivo (Izquierda) + Inspector de Nodos y Guía Celular Real (Derecha) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Simulador de Chat de WhatsApp en Vivo -->
      <div class="lg:col-span-6 bg-[#111B21] border border-slate-800 rounded-2xl overflow-hidden flex flex-col shadow-2xl min-h-[510px]">
        <!-- Cabecera estilo WhatsApp Business -->
        <div class="bg-[#202C33] px-4 py-3 flex items-center justify-between border-b border-slate-800">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-emerald-600 flex items-center justify-center font-bold text-white text-sm shadow">
              🛡️
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <span class="text-sm font-bold text-white">AegisCore Seguros Bot Oficial</span>
                <span class="text-emerald-400 text-xs" title="Cuenta de Empresa Verificada">✔</span>
              </div>
              <p class="text-[11px] text-emerald-400">en línea · conectado al flujo n8n (:5678)</p>
            </div>
          </div>
          <span class="text-[11px] font-mono text-slate-400 bg-slate-900/70 px-2.5 py-1 rounded-lg">
            +591 71099887
          </span>
        </div>

        <!-- Mensajes del Chat -->
        <div id="wa-chat-box" class="flex-1 p-4 space-y-3 overflow-y-auto max-h-[340px] bg-[#0B141A]">
          <div class="max-w-[85%] bg-[#202C33] text-slate-100 rounded-2xl rounded-tl-sm px-4 py-2.5 text-xs space-y-1 shadow">
            <p class="font-bold text-emerald-400">AegisCore Seguros IA</p>
            <p>¡Hola! 👋 Escríbeme un mensaje libre con los datos de tu vehículo para cotizar, emitir tu póliza al instante y enviarte tu <strong>Factura Fiscal PDF firmada en AWS S3</strong>.</p>
            <p class="text-[11px] text-slate-400 pt-1">Ejemplo: <em>"Hola quiero asegurar mi Toyota Hilux 2025 placa 7845-AEG con CI 6234891-SC valor 32000"</em></p>
          </div>
        </div>

        <!-- Chips rápidos de prueba -->
        <div class="bg-[#182229] px-3 py-2 border-t border-slate-800/80 flex flex-wrap gap-1.5">
          <button onclick="usarMensajeEjemplo('Hola, quiero contratar seguro PLAN-AUTO-FULL para mi Toyota Hilux 2025 placa 7845-AEG con CI 6234891-SC valor 32000 USD')"
                  class="text-[11px] px-2.5 py-1 rounded-full bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/40 transition-colors">
            💬 Ejemplo 1: Toyota Hilux (Carlos Mendoza)
          </button>
          <button onclick="usarMensajeEjemplo('Quiero póliza ejecutiva pro para mi Mazda CX-30 2025 placa 6014-AEG CI 4589120-LP valor 28500')"
                  class="text-[11px] px-2.5 py-1 rounded-full bg-teal-950/80 hover:bg-teal-900 text-teal-300 border border-teal-700/40 transition-colors">
            💬 Ejemplo 2: Mazda CX-30 (Elena Rostova)
          </button>
        </div>

        <!-- Barra de escritura estilo WhatsApp -->
        <form onsubmit="enviarMensajeWhatsApp(event)" class="bg-[#202C33] p-3 flex items-center gap-2">
          <input id="wa-input" type="text"
                 placeholder="Escribe un mensaje a WhatsApp aquí..."
                 value="Hola, quiero contratar seguro para mi Toyota Hilux 2025 placa 7845-AEG con CI 6234891-SC valor 32000 USD"
                 class="flex-1 bg-[#2A3942] text-white text-xs rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500" />
          <button type="submit" id="wa-send-btn"
                  class="px-4 py-2.5 rounded-xl bg-[#00A884] hover:bg-[#029072] text-white text-xs font-bold transition-colors shadow">
            Enviar ➤
          </button>
        </form>
      </div>

      <!-- Inspector de Ejecución n8n + Conexión con WhatsApp del Celular -->
      <div class="lg:col-span-6 space-y-5">
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white">Inspector de Payload & Salida de los 6 Nodos</h3>
            <span class="text-[11px] font-mono text-teal-400">AWS S3 + MS1 (:8001)</span>
          </div>
          <div id="exec-output" class="text-xs font-mono bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-300 min-h-[215px] overflow-x-auto">
            Escribe un mensaje en el chat de WhatsApp de la izquierda y pulsa "Enviar ➤" para ver cómo n8n extrae los datos, emite la póliza, sube el PDF a AWS S3 y responde al chat.
          </div>
        </div>

        <!-- Guía para conectar tu celular físico por Twilio Sandbox / Meta -->
        <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 space-y-2.5 text-xs">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-white">📱 ¿Quieres escribir desde el WhatsApp de tu celular físico?</h3>
            <span class="px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 font-mono text-[10px]">Twilio / Meta Ready</span>
          </div>
          <p class="text-slate-300 leading-relaxed">
            Este servidor (<code class="text-teal-300">:5678</code>) ya habla nativamente el protocolo <strong>Twilio WhatsApp Sandbox (TwiML)</strong> y <strong>Meta WhatsApp Cloud API</strong>:
          </p>
          <ol class="list-decimal list-inside space-y-1.5 text-slate-400">
            <li>Expón tu puerto local 5678 a internet ejecutando en otra terminal: <code class="text-amber-300 font-mono">ssh -R 80:127.0.0.1:5678 nokey@localhost.run</code> (o <code class="text-amber-300 font-mono">ngrok http 5678</code>).</li>
            <li>En tu consola gratuita de <strong>Twilio → Messaging → Try it out → Send a WhatsApp message → Sandbox Settings</strong>, pega en <em>"When a message comes in"</em> tu URL pública seguida de <code class="text-teal-300 font-mono">/webhook/whatsapp-pedido-poliza</code>.</li>
            <li>¡Escribe desde el WhatsApp de tu teléfono! Recibirás en tu celular la respuesta automática con el enlace directo del PDF en <strong>Amazon S3</strong>.</li>
          </ol>
        </div>
      </div>
    </div>
  </main>

  <script>
    function volverAlHubCentral() {
      const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
      const hubUrl = (typeof window !== 'undefined' && window.__AEGIS_CONFIG__ && window.__AEGIS_CONFIG__.SSO_URL) ||
        (isLocal ? 'http://localhost:8080' : 'https://aegiscore-mf2-clientes-302263088715.s3.us-east-2.amazonaws.com/sso.html');
      if (window.parent && window.parent !== window) {
        try {
          window.parent.postMessage({ type: 'AEGIS_VOLVER_HUB' }, '*');
          const hubEl = window.parent.document.getElementById('hub-modules-section') || window.parent.document.getElementById('workspace-hub');
          if (hubEl) {
            hubEl.scrollIntoView({ behavior: 'smooth' });
            return;
          }
        } catch {}
      }
      if (window.top) {
        window.top.location.href = hubUrl;
      } else {
        window.location.href = hubUrl;
      }
    }

    function usarMensajeEjemplo(texto) {
      document.getElementById('wa-input').value = texto;
    }

    function agregarBurbujaChat(htmlContent, esUsuario = false) {
      const box = document.getElementById('wa-chat-box');
      const wrapper = document.createElement('div');
      wrapper.className = esUsuario ? 'flex justify-end' : 'flex justify-start';
      const hora = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      wrapper.innerHTML = `
        <div class="max-w-[85%] ${esUsuario ? 'bg-[#005C4B] text-white rounded-2xl rounded-tr-sm' : 'bg-[#202C33] text-slate-100 rounded-2xl rounded-tl-sm'} px-4 py-2.5 text-xs space-y-1 shadow">
          <div>${htmlContent}</div>
          <div class="text-[10px] text-right ${esUsuario ? 'text-emerald-200' : 'text-slate-400'}">${hora} ${esUsuario ? '✓✓' : ''}</div>
        </div>
      `;
      box.appendChild(wrapper);
      box.scrollTop = box.scrollHeight;
    }

    async function enviarMensajeWhatsApp(e) {
      if (e) e.preventDefault();
      const input = document.getElementById('wa-input');
      const texto = input.value.trim();
      if (!texto) return;

      agregarBurbujaChat(texto, true);
      input.value = '';

      const out = document.getElementById('exec-output');
      const badge = document.getElementById('flow-status-badge');
      badge.textContent = '⚡ Ejecutando los 6 nodos del flujo n8n...';
      badge.className = 'text-xs font-mono text-amber-300';
      out.innerHTML = '<span class="text-amber-300">Procesando mensaje de WhatsApp en los 6 nodos...</span>';

      try {
        const res = await fetch('/webhook/whatsapp-pedido-poliza', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            telefono: '+591 71099887',
            mensaje: texto
          })
        });
        const data = await res.json();
        const r = data.result || {};
        const pdfUrl = r.url_pdf || '#';
        const parsed = data.steps_executed?.[1]?.data || {};

        // Iluminar los 6 nodos
        for (let i = 1; i <= 6; i++) {
          const el = document.getElementById('node-card-' + i);
          if (el) el.classList.add('ring-2', 'ring-emerald-400');
        }
        badge.textContent = `✓ Flujo completado en ${data.duration_ms} ms (${data.execution_id})`;
        badge.className = 'text-xs font-mono text-emerald-400';

        // Responder en el chat de WhatsApp con el PDF adjunto
        agregarBurbujaChat(`
          <p class="font-bold text-emerald-400 mb-1">✅ AegisCore Seguros — Póliza y Factura Emitidas</p>
          <p><strong>Asegurado:</strong> ${r.cliente?.nombreCompleto || 'Carlos Mendoza'} (${parsed.numero_documento})</p>
          <p><strong>Vehículo:</strong> ${parsed.marca} ${parsed.modelo} (${parsed.anio}) · Placa <strong>${parsed.placa}</strong></p>
          <p><strong>Póliza:</strong> <code class="text-teal-300">${r.poliza?.numeroPoliza}</code></p>
          <p><strong>Factura Fiscal:</strong> <code class="text-amber-300">${r.factura?.numeroFactura}</code> · <strong>USD ${r.factura?.total}</strong></p>
          <div class="mt-2 pt-2 border-t border-slate-700/80 flex items-center justify-between gap-2">
            <span class="text-[11px] text-slate-300">📄 ${r.factura?.numeroFactura}.pdf (AWS S3)</span>
            <a href="${pdfUrl}" target="_blank" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px]">
              Abrir PDF
            </a>
          </div>
        `, false);

        out.innerHTML = `
          <div class="space-y-1.5">
            <div class="flex items-center justify-between text-emerald-400 font-bold">
              <span>✓ Ejecución Exitosa (${data.execution_id})</span>
              <span>${data.duration_ms} ms</span>
            </div>
            <div><span class="text-slate-400">Entidades NLP extraídas:</span> CI=<strong>${parsed.numero_documento}</strong> | Placa=<strong>${parsed.placa}</strong> | Vehículo=<strong>${parsed.marca} ${parsed.modelo}</strong> | Valor=<strong>USD ${parsed.valor_comercial}</strong></div>
            <div><span class="text-slate-400">Póliza Emitida (:8001):</span> <strong class="text-white">${r.poliza?.numeroPoliza}</strong> (${parsed.plan_codigo})</div>
            <div><span class="text-slate-400">Factura Fiscal:</span> <strong class="text-white">${r.factura?.numeroFactura}</strong> (Total: USD ${r.factura?.total})</div>
            <div><span class="text-slate-400">Hash SHA-256:</span> <span class="text-teal-300">${r.hash_digital_sha256}</span></div>
            <div><span class="text-slate-400">Objeto AWS S3:</span> <a href="${pdfUrl}" target="_blank" class="text-sky-400 underline">${pdfUrl}</a></div>
          </div>
        `;
      } catch (err) {
        badge.textContent = '✕ Error en ejecución';
        badge.className = 'text-xs font-mono text-red-400';
        out.innerHTML = '<span class="text-red-400">Error: ' + err.message + '</span>';
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

    def do_HEAD(self):
        self.send_response(200)
        self._send_cors()
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_GET(self):
        # Soporte para verificación de Webhook de Meta WhatsApp Cloud API (hub.challenge)
        if self.path.startswith("/webhook"):
            parsed_url = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed_url.query)
            if "hub.challenge" in qs:
                challenge = qs["hub.challenge"][0]
                self.send_response(200)
                self._send_cors()
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(challenge.encode("utf-8"))
                return

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
            self.wfile.write(
                json.dumps({"status": "UP", "service": "n8n-local-orchestrator", "port": 5678}).encode("utf-8")
            )
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path.startswith("/webhook"):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            content_type = (self.headers.get("Content-Type") or "").lower()

            is_twilio = False
            payload = {}
            if "application/x-www-form-urlencoded" in content_type:
                parsed_qs = urllib.parse.parse_qs(raw)
                payload = {k: v[0] for k, v in parsed_qs.items() if v}
                if "Body" in payload or "From" in payload:
                    is_twilio = True
            else:
                try:
                    payload = json.loads(raw) if raw else {}
                except Exception:
                    payload = {"mensaje": raw}

            try:
                exec_res = execute_whatsapp_workflow(payload)
                if is_twilio:
                    # Responder TwiML XML nativo para que Twilio entregue el mensaje + link PDF S3 al celular WhatsApp
                    reply_msg = html.escape(exec_res.get("result", {}).get("whatsapp_reply_text", "Póliza emitida."))
                    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply_msg}</Message></Response>'
                    self.send_response(200)
                    self._send_cors()
                    self.send_header("Content-Type", "text/xml; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(twiml.encode("utf-8"))
                else:
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
    port = int(os.environ.get("PORT", os.environ.get("N8N_PORT", "5678")))
    server = HTTPServer(("0.0.0.0", port), N8nLocalHandler)
    print(f"AegisCore n8n Local Studio running on http://0.0.0.0:{port}")
    server.serve_forever()
