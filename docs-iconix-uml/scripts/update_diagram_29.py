# -*- coding: utf-8 -*-
import sqlite3
import json
import shutil
import re

# 1. Modificar build_full_project_qea.py con el nuevo diseño del diagrama 29
with open('build_full_project_qea.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_bce_classes = """        (101, 7, "Component", "Nivel 1: Frontend", "App Móvil Flutter (SQLite + TFLite)"),
        (102, 7, "Component", "Nivel 1: Frontend", "Portal Clientes React PWA (ONNX Local)"),
        (103, 7, "Component", "Nivel 1: Frontend", "Panel Admin Angular 17+ (Dashboards BI)"),
        (104, 7, "Component", "Nivel 2: Backend", "MS1 Pólizas y Clientes PHP Laravel (DDD)"),
        (105, 7, "Component", "Nivel 2: Backend", "MS2 Siniestros y Triaje NestJS (Clean/CQRS)"),
        (106, 7, "Component", "Nivel 2: Backend", "MS3 Motor Actuarial Spring Boot (Hexagonal)"),
        (107, 7, "Component", "Nivel 2: Backend", "MS4 IA, Agentes y Servidor MCP FastAPI"),
        (108, 7, "Node", "Nivel 3: Persistencia", "Persistencia Políglota (PG, Mongo, DynamoDB, Redis)"),
        (109, 7, "Node", "Nivel 4: Mensajería", "Apache Kafka & Apollo Supergraph Router")"""

new_bce_classes = """        # Componentes Nivel 1 a 4 Desglosados (IDs 101 al 120)
        (101, 7, "Component", "Nivel 1: Frontend", "App Móvil Flutter (SQLite + TFLite)"),
        (102, 7, "Component", "Nivel 1: Frontend", "Portal Clientes React 18+ PWA (IA Local Web)"),
        (103, 7, "Component", "Nivel 1: Frontend", "Panel Admin Angular 17+ (Dashboards BI Nativos)"),
        (110, 7, "Component", "Nivel 1: Frontend", "SSO Shell Container (Keycloak JS)"),
        (111, 7, "Component", "Nivel Gateways", "Keycloak SSO 24 (OAuth2 / OIDC + PKCE)"),
        (112, 7, "Component", "Nivel Gateways", "Apollo Supergraph Router 2.5 (GraphQL Federation)"),
        (113, 7, "Component", "Nivel Gateways", "Servidor MCP Protocol (Blindaje OWASP Anti-SQLi)"),
        (104, 7, "Component", "Nivel 2: Backend", "MS1 Pólizas y Facturación (PHP 8.3 Laravel - DDD)"),
        (105, 7, "Component", "Nivel 2: Backend", "MS2 Siniestros y Triaje (NestJS 10 - Clean CQRS)"),
        (106, 7, "Component", "Nivel 2: Backend", "MS3 Motor Actuarial y Pagos (Spring Boot 3 - Hexagonal)"),
        (107, 7, "Component", "Nivel 2: Backend", "MS4 Inteligencia Artificial y Agentes (Python FastAPI)"),
        (114, 7, "Component", "Nivel 3: Persistencia", "PostgreSQL 16 Relacional ACID (aegiscore_erp)"),
        (115, 7, "Component", "Nivel 3: Persistencia", "MongoDB 7.0 Documental BSON (Índice 2dsphere)"),
        (116, 7, "Component", "Nivel 3: Persistencia", "Amazon DynamoDB Local (IdempotencyRecords < 5ms)"),
        (117, 7, "Component", "Nivel 3: Persistencia", "SQLite 3 Móvil Cifrado (Offline Flutter)"),
        (118, 7, "Component", "Nivel 3: Persistencia", "Redis Cache 7 (Subgrafos y Sesiones)"),
        (119, 7, "Component", "Nivel 4: Mensajería", "Apache Kafka 3.7 Bus de Eventos (saga-claim-settlement)"),
        (120, 7, "Component", "Nivel 4: Automatización", "Servidor Automatización n8n (WhatsApp / Facturas PDF)")"""

old_comp_layout = """    # --- Diagrama 30: Componentes y Arquitectura Global en 4 Niveles ---
    comp_layout = [
        (101, 50, 50, 260, 160),   # Flutter
        (102, 50, 220, 260, 330),  # React PWA
        (103, 50, 390, 260, 500),  # Angular Admin
        (104, 350, 50, 580, 160),  # MS1 PHP
        (105, 350, 220, 580, 330), # MS2 NestJS
        (106, 350, 390, 580, 500), # MS3 Spring Boot
        (107, 350, 560, 580, 670), # MS4 Python FastAPI
        (108, 680, 220, 920, 380), # Persistencia Poliglota
        (109, 980, 220, 1220, 380) # Kafka y Gateway
    ]
    for cid, l, t, r, b in comp_layout:
        add_dobj(30, cid, l, t, r, b)
    add_conn("HTTP REST Idempotente", "Dependency", 101, 105, 30)
    add_conn("Consulta GraphQL", "Dependency", 102, 104, 30)
    add_conn("BI Dashboards", "Dependency", 103, 107, 30)
    add_conn("ACID PostgreSQL", "Association", 104, 108, 30)
    add_conn("MongoDB 2dsphere", "Association", 105, 108, 30)
    add_conn("Hexagonal JPA", "Association", 106, 108, 30)
    add_conn("ML Scikit/TF", "Association", 107, 108, 30)
    add_conn("Saga Bus Eventos", "Association", 106, 109, 30)
    add_conn("Compensacion Kafka", "Dependency", 109, 104, 30)
    add_conn("Reversión Kafka", "Dependency", 109, 105, 30)"""

new_comp_layout = """    # --- Diagrama 30: Componentes y Arquitectura Global en 4 Niveles Desglosada (18 Componentes en 5 Columnas) ---
    comp_layout = [
        # Columna 1: Frontends & Clientes (X: 40 a 270)
        (101, 40, 50, 270, 150),    # Flutter Móvil
        (102, 40, 190, 270, 290),   # React PWA
        (103, 40, 330, 270, 430),   # Angular Admin BI
        (110, 40, 470, 270, 570),   # SSO Shell Container
        
        # Columna 2: Gateways & Seguridad (X: 330 a 570)
        (111, 330, 50, 570, 150),   # Keycloak SSO
        (112, 330, 220, 570, 330),  # Apollo Supergraph Router
        (113, 330, 400, 570, 510),  # Servidor MCP Protocol
        
        # Columna 3: Microservicios Backend (X: 630 a 890)
        (104, 630, 50, 890, 150),   # MS1 PHP Laravel DDD
        (105, 630, 190, 890, 290),  # MS2 NestJS Clean CQRS
        (106, 630, 330, 890, 430),  # MS3 Spring Boot Hexagonal
        (107, 630, 470, 890, 570),  # MS4 Python FastAPI IA
        
        # Columna 4: Persistencia Políglota Individual (X: 950 a 1220)
        (114, 950, 50, 1220, 140),  # PostgreSQL 16
        (115, 950, 170, 1220, 260), # MongoDB 7
        (116, 950, 290, 1220, 380), # DynamoDB Local
        (118, 950, 410, 1220, 500), # Redis Cache
        (117, 950, 530, 1220, 620), # SQLite 3 Móvil
        
        # Columna 5: Mensajería Asíncrona y Automatización (X: 1280 a 1540)
        (119, 1280, 160, 1540, 290), # Apache Kafka
        (120, 1280, 350, 1540, 480)  # n8n Automation
    ]
    for cid, l, t, r, b in comp_layout:
        add_dobj(30, cid, l, t, r, b)

    # Conectores Ortogonales Limpios
    # Nivel 1 a Gateways y Almacenamiento Local
    add_conn("Auth PKCE", "Dependency", 110, 111, 30)
    add_conn("Queries / Mutations", "Dependency", 102, 112, 30)
    add_conn("Audio WebRTC / Tools", "Dependency", 103, 113, 30)
    add_conn("HTTP REST Idempotente", "Dependency", 101, 105, 30)
    add_conn("Persistencia Offline", "Dependency", 101, 117, 30)

    # Gateways a Microservicios Backend
    add_conn("Subgrafo Pólizas", "Dependency", 112, 104, 30)
    add_conn("Subgrafo Siniestros", "Dependency", 112, 105, 30)
    add_conn("Subgrafo Actuarial", "Dependency", 112, 106, 30)
    add_conn("Tools Tipadas MCP", "Dependency", 113, 107, 30)

    # Microservicios a Persistencia Políglota
    add_conn("ACID PostgreSQL", "Association", 104, 114, 30)
    add_conn("Caché Consultas", "Association", 104, 118, 30)
    add_conn("MongoDB 2dsphere", "Association", 105, 115, 30)
    add_conn("Check Idempotencia <5ms", "Association", 105, 116, 30)
    add_conn("JPA Transaccional", "Association", 106, 114, 30)
    add_conn("Lock Idempotencia QR", "Association", 106, 116, 30)
    add_conn("Dataset Histórico 1,200 Regs", "Association", 107, 114, 30)
    add_conn("Expedientes BSON", "Association", 107, 115, 30)

    # Microservicios a Mensajería y Automatización
    add_conn("Eventos Siniestros", "Association", 105, 119, 30)
    add_conn("Orquestación Saga CU09", "Association", 106, 119, 30)
    add_conn("Reserva Cobertura", "Association", 104, 119, 30)
    add_conn("Webhook Pedido WhatsApp", "Dependency", 120, 104, 30)
    add_conn("Webhook Siniestro SOS", "Dependency", 120, 105, 30)"""

code = code.replace(old_bce_classes, new_bce_classes)
code = code.replace(old_comp_layout, new_comp_layout)

with open('build_full_project_qea.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("build_full_project_qea.py actualizado con éxito.")

