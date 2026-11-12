import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import {
  Cliente,
  PlanSeguro,
  Poliza,
  ResumenUnificadoPayload,
  CotizacionResultado,
  ResultadoValidacionNitidezLocal,
  ColaSincronizacionOfflineItem,
  TipoPlan,
  RolSSO
} from './core/models/aegiscore.models';
import { ValidadorNitidezLocalWebControl } from './core/ai/ValidadorNitidezLocalWebControl';
import { AuthOIDCService, PERFILES_SSO_DEMO, PerfilSSOActivo } from './core/auth/AuthOIDCService';
import { ApolloFederationClient } from './core/graphql/ApolloFederationClient';

const isLocalEnv = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const CLOUD_MS1_URL = 'https://aegiscore-ms1-polizas-jskh4rw62q-uc.a.run.app';
const CLOUD_SSO_HUB = 'https://aegiscore-mf2-clientes-302263088715.s3.us-east-2.amazonaws.com/sso.html';

const MS1_PUBLIC_URL = (import.meta as any)?.env?.VITE_MS1_URL || (typeof window !== 'undefined' && (window as any).__AEGIS_MS1_URL) || (isLocalEnv ? 'http://localhost:8001' : CLOUD_MS1_URL);

type ActiveTab = 'resumen' | 'cotizador' | 'catalogo' | 'facturacion_qr' | 'seguridad';

export const App: React.FC = () => {
  const authService = useMemo(() => new AuthOIDCService(), []);
  const apolloClient = useMemo(() => new ApolloFederationClient(), []);
  const validadorIA = useMemo(() => new ValidadorNitidezLocalWebControl(), []);
  const docCanvasRef = useRef<HTMLCanvasElement | null>(null);

  const [activeTab, setActiveTab] = useState<ActiveTab>('resumen');
  const [isOffline, setIsOffline] = useState<boolean>(() =>
    typeof navigator !== 'undefined' ? !navigator.onLine : false
  );
  const [manualOfflineMode, setManualOfflineMode] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<{ type: 'success' | 'warning' | 'error'; text: string } | null>(null);
  const resumenCacheRef = useRef<Record<string, ResumenUnificadoPayload>>({});

  // Estado de Sesión e Identidad (CU01)
  const [sesionSSO, setSesionSSO] = useState<PerfilSSOActivo | null>(() => authService.obtenerSesionInicial());
  const [authChecked, setAuthChecked] = useState<boolean>(false);
  const [clienteActivoId, setClienteActivoId] = useState<string>('b0000001-0000-0000-0000-000000000001');
  const [sesionesSSOList, setSesionesSSOList] = useState<
    Array<{
      session_id: string;
      keycloak_sub: string;
      email?: string;
      nombre_completo?: string;
      rol: string;
      dispositivo?: string;
      token_sha256: string;
      status: string;
      created_at: string;
    }>
  >([]);
  const [customLoginForm, setCustomLoginForm] = useState({
    email: 'carlos.mendoza@gmail.com',
    rol: 'CLIENTE'
  });
  const [mostrarInspectorJwt, setMostrarInspectorJwt] = useState<boolean>(true);

  // Estado de Resumen de Pólizas, Coberturas, Certificados S3 y Siniestros (CU02)
  const [resumenUnificado, setResumenUnificado] = useState<ResumenUnificadoPayload | null>(null);
  // Mapa independiente por ID de póliza para que editar una póliza no cambie las demás
  const [montosAjustePorPoliza, setMontosAjustePorPoliza] = useState<Record<string, number>>({});
  const [filtroBusquedaResumen, setFiltroBusquedaResumen] = useState<string>('');
  const [coberturasExpandidasPorPoliza, setCoberturasExpandidasPorPoliza] = useState<Record<string, boolean>>({});
  const [certificadosS3PorPoliza, setCertificadosS3PorPoliza] = useState<
    Record<string, { urlPdf: string; s3Url?: string | null; hashSha256: string }>
  >({});

  // Estado de Catálogo de Planes, Coberturas y Clientes
  const [planes, setPlanes] = useState<PlanSeguro[]>([]);
  const [clientesList, setClientesList] = useState<Cliente[]>([]);
  const [filtroRamoPlan, setFiltroRamoPlan] = useState<string>('TODOS');
  const [busquedaPlanes, setBusquedaPlanes] = useState<string>('');
  const [busquedaClientes, setBusquedaClientes] = useState<string>('');
  const [nuevoPlanForm, setNuevoPlanForm] = useState({
    codigo: 'PLAN-EJECUTIVO-PLUS',
    nombre: 'Cobertura Todo Riesgo Ejecutivo Plus',
    tipo: 'VEHICULAR' as TipoPlan,
    primaBaseAnual: 690,
    deducibleBasePorcentaje: 10,
    descripcion: 'Protección integral frente a colisiones, granizo, robo total, responsabilidad civil y asistencia vial 24/7.'
  });
  const [nuevaCoberturaForm, setNuevaCoberturaForm] = useState({
    planId: 'a0000001-0000-0000-0000-000000000001',
    codigo: 'COB-GRANIZO-2026',
    nombre: 'Daños por Granizo e Inundación Urbana',
    sumaAseguradaMax: 15000,
    deducibleMinimo: 120,
    deduciblePorcentaje: 5
  });
  const [nuevoClienteForm, setNuevoClienteForm] = useState({
    tipoDocumento: 'CI',
    numeroDocumento: '8391045-CB',
    nombres: 'Roberto Carlos',
    apellidos: 'Gutiérrez Pinto',
    email: 'roberto.gutierrez@empresa.bo',
    telefono: '+591 76543210',
    ciudad: 'Cochabamba',
    scoreCrediticio: 835
  });

  // Estado de Cotizador y Escáner Inteligente de Documentos
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [camaraActiva, setCamaraActiva] = useState<boolean>(false);
  const [vistaMapaBordes, setVistaMapaBordes] = useState<boolean>(false);
  const imagenOriginalBackupRef = useRef<ImageData | null>(null);
  const [isDraggingDoc, setIsDraggingDoc] = useState<boolean>(false);
  const [documentoS3Info, setDocumentoS3Info] = useState<{
    s3Url: string;
    hashSha256: string;
    bucket: string;
    key: string;
  } | null>(null);

  const [cotizadorForm, setCotizadorForm] = useState({
    planId: 'a0000001-0000-0000-0000-000000000001',
    tipoPlan: 'VEHICULAR' as TipoPlan,
    edadConductor: 34,
    ciudad: 'Santa Cruz',
    placa: '5892-TXR',
    vin: 'JTEBU5JR9K5109283',
    marca: 'Toyota',
    modelo: 'Corolla Cross Hybrid',
    anio: 2025,
    color: 'Blanco Perlado',
    valorComercial: 26500
  });
  const [cotizacionActual, setCotizacionActual] = useState<CotizacionResultado | null>(null);
  const [validacionNitidez, setValidacionNitidez] = useState<ResultadoValidacionNitidezLocal | null>(null);
  const [modoEscaneoActual, setModoEscaneoActual] = useState<'NITIDA_HD' | 'BORROSA_DESENFOCADA'>('NITIDA_HD');
  const [polizaRecienEmitida, setPolizaRecienEmitida] = useState<Poliza | null>(null);
  const [colaOffline, setColaOffline] = useState<ColaSincronizacionOfflineItem[]>(() =>
    apolloClient.obtenerColaOffline()
  );

  // Referencia para desplazamiento suave hacia la Pasarela Bancaria QR
  const pasarelaQrSectionRef = useRef<HTMLDivElement | null>(null);

  // Estado de Contratación Digital WhatsApp, Facturación PDF y Cobro QR Sandbox
  const [whatsappForm, setWhatsappForm] = useState({
    telefono: '+591 71099887',
    numero_documento: '6234891-SC',
    placa: '6014-AEG',
    marca: 'Mazda',
    modelo: 'CX-30 AWD',
    anio: 2025,
    valor_comercial: 28000,
    plan_codigo: 'PLAN-AUTO-FULL',
    tipo_comprobante: 'FACTURA' as 'FACTURA' | 'NOTA_VENTA'
  });
  const [pedidoWhatsAppResult, setPedidoWhatsAppResult] = useState<{
    status: string;
    mensaje_whatsapp: string;
    poliza: Poliza;
    factura: {
      id: string;
      numeroFactura: string;
      subtotal: number;
      impuestos: number;
      total: number;
      moneda: string;
      tipoComprobante: string;
    };
    url_pdf: string;
    hash_digital_sha256: string;
  } | null>(null);

  // Estado funcional de Pasarela Sandbox QR
  const [qrForm, setQrForm] = useState({
    polizaId: 'd0000001-0000-0000-0000-000000000001',
    facturaId: 'f0000001-0000-0000-0000-000000000001',
    numeroCuota: 1,
    monto: 60.0,
    bancoSandbox: 'Banco Nacional de Bolivia (BNB · SIP QR Sandbox)'
  });
  const [qrKeyUuid, setQrKeyUuid] = useState<string>(() => ApolloFederationClient.generarUUIDv4());
  const [qrPagoResult, setQrPagoResult] = useState<{
    id: string;
    polizaId: string;
    facturaId?: string | null;
    numeroCuota: number;
    monto: number;
    moneda: string;
    idempotencyKey: string;
    qrImagenPayload: string;
    estado: string;
    codigoAutorizacion: string;
    bancoSandbox?: string;
    sandboxVoucherUrl?: string;
    fechaPago: string;
    fueIdempotente: boolean;
    cacheHit: string;
  } | null>(null);
  const [historialPagosQr, setHistorialPagosQr] = useState<
    Array<{
      id: string;
      polizaId: string;
      facturaId?: string | null;
      numeroCuota: number;
      monto: number;
      moneda: string;
      idempotencyKey: string;
      codigoAutorizacion: string;
      bancoSandbox?: string;
      estado: string;
      fechaPago: string;
    }>
  >([]);

  const showToast = useCallback((type: 'success' | 'warning' | 'error', text: string) => {
    setToastMessage({ type, text });
    setTimeout(() => setToastMessage(null), 4500);
  }, []);

  // Dibuja vista previa realista del documento RUAT / Cédula en el Canvas
  const renderizarVistaPreviaDocumento = useCallback(
    (modo: 'NITIDA_HD' | 'BORROSA_DESENFOCADA', placa: string, marca: string, modelo: string) => {
      const canvas = docCanvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();

      if (modo === 'BORROSA_DESENFOCADA') {
        ctx.filter = 'blur(3.6px) contrast(0.75)';
      } else {
        ctx.filter = 'none';
      }

      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = '#005C55';
      ctx.fillRect(0, 0, canvas.width, 34);

      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.fillText('CERTIFICADO DE REGISTRO VEHICULAR · RUAT', 14, 21);

      ctx.strokeStyle = '#CBD5E1';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(10, 42, canvas.width - 20, canvas.height - 52);

      ctx.fillStyle = '#F1F5F9';
      ctx.fillRect(20, 52, 74, 80);
      ctx.strokeStyle = '#94A3B8';
      ctx.strokeRect(20, 52, 74, 80);

      ctx.fillStyle = '#0F172A';
      ctx.font = 'bold 12px JetBrains Mono, monospace';
      ctx.fillText(placa, 26, 94);

      ctx.fillStyle = '#64748B';
      ctx.font = '600 9px Inter, sans-serif';
      ctx.fillText('PROPIETARIO TITULAR', 106, 62);
      ctx.fillStyle = '#0F172A';
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.fillText((resumenUnificado?.cliente.nombreCompleto || 'CARLOS MENDOZA ROCA').toUpperCase().slice(0, 24), 106, 76);

      ctx.fillStyle = '#64748B';
      ctx.font = '600 9px Inter, sans-serif';
      ctx.fillText('VEHÍCULO / CLASE', 106, 96);
      ctx.fillStyle = '#0F172A';
      ctx.font = 'bold 11px Inter, sans-serif';
      ctx.fillText(`${marca.toUpperCase()} ${modelo.toUpperCase()}`.slice(0, 24), 106, 110);

      ctx.fillStyle = '#0F172A';
      for (let x = 20; x < canvas.width - 24; x += 5) {
        const barW = x % 10 === 0 ? 3 : 1.5;
        ctx.fillRect(x, 140, barW, 16);
      }

      ctx.restore();
    },
    [resumenUnificado?.cliente.nombreCompleto]
  );

  const sincronizarEstadoResumen = useCallback((payload: ResumenUnificadoPayload) => {
    resumenCacheRef.current[payload.cliente.id] = payload;
    setResumenUnificado(payload);
    setMontosAjustePorPoliza((prev) => {
      const next = { ...prev };
      for (const p of payload.polizasActivas) {
        if (next[p.id] === undefined) {
          next[p.id] = 3200;
        }
      }
      return next;
    });

    const primeraPoliza = payload.polizasActivas[0];
    const primeraFactura = payload.pagosPendientes[0];
    if (primeraPoliza) {
      setQrForm((prev) => ({
        ...prev,
        polizaId: primeraPoliza.id,
        facturaId: primeraFactura?.id || '',
        monto: primeraPoliza.primaMensual || 60.0
      }));
    }
  }, []);

  const cargarDatosIniciales = useCallback(async (targetClienteId?: string, overrideToken?: string) => {
    const cid = targetClienteId ?? clienteActivoId;
    const token = overrideToken ?? sesionSSO?.access_token ?? '';
    setLoading(true);
    try {
      const [resumenResp, catalogoResp, pagosQrResp, ssoSessionsResp] = await Promise.all([
        apolloClient.consultarResumenUnificadoAsegurado(cid, token),
        apolloClient.listarCatalogoYClientes(token),
        apolloClient.listarPagosQrRegistrados(),
        apolloClient.listarSesionesSSO()
      ]);

      sincronizarEstadoResumen(resumenResp.payload);
      setPlanes(catalogoResp.planes);
      setClientesList(catalogoResp.clientes);
      setHistorialPagosQr(pagosQrResp);
      setSesionesSSOList(ssoSessionsResp);

      const tensorHD = validadorIA.generarTensorSimulado('NITIDA_HD', 96, 64);
      const resIA = validadorIA.validarNitidez(tensorHD.pixels, tensorHD.width, tensorHD.height, {
        tipoDoc: 'Certificado RUAT + Cédula',
        placa: '5892-TXR'
      });
      setValidacionNitidez((prev) => prev ?? resIA);
    } finally {
      setLoading(false);
    }
  }, [apolloClient, clienteActivoId, sesionSSO?.access_token, sincronizarEstadoResumen, validadorIA]);

  // Pestañas disponibles según el rol institucional gobernado por OIDC
  const tabsDisponibles = useMemo(() => {
    const rol = sesionSSO?.rol || 'CLIENTE';
    if (rol === 'CLIENTE') {
      return [
        { id: 'resumen', label: 'Mi Póliza y Cobertura', icon: 'verified_user' },
        { id: 'cotizador', label: 'Cotizar y Emitir Póliza', icon: 'document_scanner' },
        { id: 'facturacion_qr', label: 'Facturación y Pagos QR', icon: 'qr_code_2' },
        { id: 'seguridad', label: 'Cuenta y Seguridad', icon: 'shield_lock' }
      ];
    }
    if (rol === 'PERITO') {
      return [
        { id: 'resumen', label: 'Inspección de Pólizas', icon: 'verified_user' },
        { id: 'cotizador', label: 'Verificador de Nitidez IA', icon: 'document_scanner' },
        { id: 'seguridad', label: 'Cuenta y Seguridad', icon: 'shield_lock' }
      ];
    }
    // ACTUARIO y ADMIN
    return [
      { id: 'resumen', label: 'Mi Póliza y Cobertura', icon: 'verified_user' },
      { id: 'cotizador', label: 'Cotizar y Emitir Póliza', icon: 'document_scanner' },
      { id: 'catalogo', label: 'Planes y Asegurados', icon: 'workspace_premium' },
      { id: 'facturacion_qr', label: 'Facturación y Pagos QR', icon: 'qr_code_2' },
      { id: 'seguridad', label: 'Cuenta y Seguridad', icon: 'shield_lock' }
    ];
  }, [sesionSSO?.rol]);

  useEffect(() => {
    if (tabsDisponibles.length > 0 && !tabsDisponibles.some((t) => t.id === activeTab)) {
      setActiveTab('resumen');
    }
  }, [tabsDisponibles, activeTab]);

  // Carga inicial autoritativa: Consulta sesión única distribuida en DynamoDB
  const initialLoadDoneRef = useRef<boolean>(false);
  useEffect(() => {
    if (!initialLoadDoneRef.current) {
      initialLoadDoneRef.current = true;
      const params = new URLSearchParams(window.location.search);
      const handoffEmail = params.get('sso_email');
      const handoffRol = params.get('sso_rol') as RolSSO | null;

      authService.sincronizarConSesionActivaRemota(handoffEmail, handoffRol)
        .then((nuevoPerfil) => {
          setAuthChecked(true);
          if (!nuevoPerfil) {
            setSesionSSO(null);
            // Redirección automática si se abre directamente fuera de iframe
            if (window.self === window.top) {
              setTimeout(() => {
                window.location.href = obtenerSsoHubUrl();
              }, 1800);
            }
            return;
          }

          setSesionSSO(nuevoPerfil);
          if (nuevoPerfil.cliente_id) {
            setClienteActivoId(nuevoPerfil.cliente_id);
            cargarDatosIniciales(nuevoPerfil.cliente_id, nuevoPerfil.access_token);
          } else {
            cargarDatosIniciales(undefined, nuevoPerfil.access_token);
          }
          apolloClient.listarSesionesSSO().then(setSesionesSSOList);
          if (handoffEmail) {
            showToast('success', `Sesión corporativa propagada: ${nuevoPerfil.nombre_completo} (${nuevoPerfil.rol}).`);
          }
        })
        .catch((err) => {
          console.warn('[React App] Error al sincronizar sesión SSO remota:', err);
          setAuthChecked(true);
          const fallback = authService.obtenerPerfilPorDefecto();
          setSesionSSO(fallback);
          cargarDatosIniciales(fallback.cliente_id, fallback.access_token);
        });
    }
  }, [apolloClient, authService, cargarDatosIniciales, showToast]);

  // =========================================================================
  // DETECCIÓN AUTOMÁTICA EN TIEMPO REAL DE CORTE DE INTERNET (ONLINE / OFFLINE)
  // =========================================================================
  useEffect(() => {
    let isMounted = true;

    const verificarConexionInternetReal = async (): Promise<boolean> => {
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        return false;
      }
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 2500);
        // Probe ligero a DNS público de Google con CORS para detectar caída real de Wi-Fi/Internet
        // incluso cuando localhost sigue activo en la misma máquina
        const res = await fetch('https://dns.google/resolve?name=example.com&type=A', {
          method: 'GET',
          cache: 'no-store',
          signal: controller.signal
        });
        clearTimeout(timer);
        return res.ok;
      } catch {
        return false;
      }
    };

    const handleBrowserOffline = () => {
      if (!isMounted) return;
      setIsOffline(true);
      showToast('warning', 'Se detectó desconexión de Internet: Modo sin conexión activado automáticamente.');
    };

    const handleBrowserOnline = async () => {
      if (!isMounted || manualOfflineMode) return;
      const tieneInternet = await verificarConexionInternetReal();
      if (tieneInternet && isMounted) {
        setIsOffline(false);
        const token = sesionSSO?.access_token || '';
        const actualizada = await apolloClient.sincronizarColaOffline(token);
        setColaOffline(actualizada);
        showToast('success', 'Conexión a Internet restablecida: Datos sincronizados.');
      }
    };

    window.addEventListener('offline', handleBrowserOffline);
    window.addEventListener('online', handleBrowserOnline);

    // Monitoreo continuo cada 4 segundos para detectar desconexión de Wi-Fi al instante
    const intervalId = setInterval(async () => {
      if (manualOfflineMode) return;
      const onlineReal = await verificarConexionInternetReal();
      if (!isMounted) return;

      setIsOffline((prevOffline) => {
        if (!onlineReal && !prevOffline) {
          showToast('warning', 'Corte de Internet detectado: Operando en modo sin conexión.');
          return true;
        }
        if (onlineReal && prevOffline) {
          const token = sesionSSO?.access_token || '';
          apolloClient.sincronizarColaOffline(token).then((act) => {
            if (isMounted) setColaOffline(act);
          });
          showToast('success', 'Internet restablecido: Sincronización en línea activa.');
          return false;
        }
        return prevOffline;
      });
    }, 4000);

    return () => {
      isMounted = false;
      window.removeEventListener('offline', handleBrowserOffline);
      window.removeEventListener('online', handleBrowserOnline);
      clearInterval(intervalId);
    };
  }, [apolloClient, manualOfflineMode, sesionSSO?.access_token, showToast]);

  useEffect(() => {
    if (activeTab === 'cotizador' && !camaraActiva) {
      renderizarVistaPreviaDocumento(
        modoEscaneoActual,
        cotizadorForm.placa,
        cotizadorForm.marca,
        cotizadorForm.modelo
      );
    }
  }, [activeTab, camaraActiva, modoEscaneoActual, cotizadorForm.placa, cotizadorForm.marca, cotizadorForm.modelo, renderizarVistaPreviaDocumento]);

  // Conexión del stream de cámara web al elemento <video>
  useEffect(() => {
    if (camaraActiva && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {});
    }
  }, [camaraActiva]);

  // Limpieza de cámara web al cambiar de pestaña o desmontar
  useEffect(() => {
    if (activeTab !== 'cotizador' && streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setCamaraActiva(false);
    }
  }, [activeTab]);

  // Alternar Modo Online / Sin Conexión Manualmente
  const handleToggleOffline = async () => {
    const nextOffline = !isOffline;
    setIsOffline(nextOffline);
    setManualOfflineMode(nextOffline);
    if (!nextOffline) {
      const token = sesionSSO?.access_token || '';
      const actualizada = await apolloClient.sincronizarColaOffline(token);
      setColaOffline(actualizada);
      showToast('success', 'Conexión restablecida: Las operaciones pendientes han sido sincronizadas.');
      await cargarDatosIniciales();
    } else {
      showToast('warning', 'Modo sin conexión activado: Las solicitudes se guardarán localmente de forma segura.');
    }
  };

  // Cambiar Asegurado Activo (con caché instantáneo 0ms + actualización ligera de 1 sola consulta)
  const handleSelectClienteActivo = async (nuevoId: string) => {
    if (nuevoId === clienteActivoId || pendingAction === 'switch-client') return;
    setClienteActivoId(nuevoId);

    const cli = clientesList.find((c) => c.id === nuevoId);
    if (cli) {
      setWhatsappForm((prev) => ({
        ...prev,
        numero_documento: cli.numeroDocumento,
        telefono: cli.telefono || '+591 71099887'
      }));
    }

    // Si ya está en caché local de la sesión, mostrar de inmediato en 0ms mientras refresca
    const cached = resumenCacheRef.current[nuevoId];
    if (cached) {
      sincronizarEstadoResumen(cached);
    }

    setPendingAction('switch-client');
    try {
      const token = sesionSSO?.access_token || '';
      const resumenResp = await apolloClient.consultarResumenUnificadoAsegurado(nuevoId, token);
      sincronizarEstadoResumen(resumenResp.payload);
      showToast(
        'success',
        `Asegurado activo cambiado a ${resumenResp.payload.cliente.nombreCompleto} (${resumenResp.payload.cliente.numeroDocumento}).`
      );
    } finally {
      setPendingAction(null);
    }
  };

  // Cambiar Perfil de Usuario Activo (CU01)
  const handleSwitchSSOUser = async (email: string, rol?: string) => {
    if (pendingAction) return;
    setPendingAction(`sso-${email}`);
    setLoading(true);
    try {
      const nuevoPerfil = await authService.autenticarUsuarioOIDC(email, rol as PerfilSSOActivo['rol']);
      setSesionSSO(nuevoPerfil);
      const sesionesActualizadas = await apolloClient.listarSesionesSSO();
      setSesionesSSOList(sesionesActualizadas);
      showToast('success', `Sesión corporativa iniciada como ${nuevoPerfil.nombre_completo} (${nuevoPerfil.rol}).`);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  const obtenerSsoHubUrl = useCallback(() => {
    if (typeof window !== 'undefined' && (window as any).__AEGIS_SSO_URL) {
      return (window as any).__AEGIS_SSO_URL;
    }
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    return isLocal ? 'http://localhost:8080' : CLOUD_SSO_HUB;
  }, []);

  const volverAlHubCentral = useCallback(() => {
    const ssoUrl = obtenerSsoHubUrl();
    if (typeof window !== 'undefined') {
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
        window.top.location.href = ssoUrl;
      } else {
        window.location.href = ssoUrl;
      }
    }
  }, [obtenerSsoHubUrl]);

  const handleCustomLoginSSO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customLoginForm.email.trim()) return;
    await handleSwitchSSOUser(customLoginForm.email.trim(), customLoginForm.rol);
  };

  const handleCerrarSesionSSO = async (sessionId = 'ALL') => {
    if (pendingAction) return;
    setPendingAction(`logout-${sessionId}`);
    try {
      await authService.cerrarSesionSSO();
      setSesionSSO(null);
      showToast('warning', 'Sesión corporativa cerrada. Redirigiendo a Bóveda Central...');
      setTimeout(() => {
        window.location.href = obtenerSsoHubUrl();
      }, 400);
    } catch {
      window.location.href = obtenerSsoHubUrl();
    } finally {
      setPendingAction(null);
    }
  };

  // Generar y Abrir Certificado Oficial de Póliza en Amazon S3 (CU02)
  const handleDescargarCertificadoPolizaS3 = async (polizaId: string, numeroPoliza: string) => {
    if (pendingAction) return;
    const actionKey = `cert-${polizaId}`;
    setPendingAction(actionKey);
    try {
      const cert = await apolloClient.generarCertificadoPolizaS3(polizaId);
      setCertificadosS3PorPoliza((prev) => ({
        ...prev,
        [polizaId]: {
          urlPdf: cert.urlPdf,
          s3Url: cert.s3Url,
          hashSha256: cert.hashSha256
        }
      }));
      window.open(cert.s3Url || cert.urlPdf, '_blank', 'noopener,noreferrer');
      showToast(
        'success',
        `Certificado ${cert.filename} generado y publicado en Amazon S3 (${numeroPoliza}).`
      );
    } catch {
      window.open(`${MS1_PUBLIC_URL}/api/v1/polizas/${encodeURIComponent(polizaId)}/certificado-pdf`, '_blank', 'noopener,noreferrer');
    } finally {
      setPendingAction(null);
    }
  };

  const jwtDecodificado = useMemo(() => {
    try {
      const parts = (sesionSSO?.access_token || '').split('.');
      if (parts.length === 3) {
        const header = JSON.parse(atob(parts[0].replace(/-/g, '+').replace(/_/g, '/')));
        const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
        return { header, payload };
      }
    } catch {
      // Fallback
    }
    return {
      header: { alg: 'RS256', typ: 'JWT', kid: 'aegiscore-keycloak-rs256-key-2026' },
      payload: {
        iss: 'http://localhost:8080/realms/aegiscore',
        sub: sesionSSO?.keycloak_sub || 'kc-cliente-001',
        name: sesionSSO?.nombre_completo || 'Carlos Mendoza Roca',
        email: sesionSSO?.email || 'carlos.mendoza@gmail.com',
        rol: sesionSSO?.rol || 'CLIENTE',
        pkce_challenge_method: 'S256',
        pkce_verified: true
      }
    };
  }, [sesionSSO]);

  // Ajuste y Reversión de Cobertura (usa el monto individual de la póliza seleccionada + actualización optimista inmediata)
  const handleAjusteCobertura = async (accion: 'descontar-cobertura' | 'compensar-cobertura', polizaId: string) => {
    if (pendingAction) return;
    const montoIndividual = montosAjustePorPoliza[polizaId] ?? 3200;
    const actionKey = `${accion}-${polizaId}`;
    setPendingAction(actionKey);
    try {
      await apolloClient.ejecutarAccionSagaMS1(accion, polizaId, montoIndividual);
      const token = sesionSSO?.access_token || '';
      const resumenResp = await apolloClient.consultarResumenUnificadoAsegurado(clienteActivoId, token);
      sincronizarEstadoResumen(resumenResp.payload);
      if (accion === 'descontar-cobertura') {
        showToast('success', `Se aplicó el descuento por indemnización de USD ${montoIndividual.toLocaleString()} sobre la póliza seleccionada.`);
      } else {
        showToast('warning', `Reversión completada: Se restituyeron USD ${montoIndividual.toLocaleString()} al saldo disponible de la póliza.`);
      }
    } catch {
      showToast('warning', 'Actualización de saldo de cobertura aplicada.');
    } finally {
      setPendingAction(null);
    }
  };

  // Gestión de Planes, Coberturas y Clientes
  const handleCrearPlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pendingAction) return;
    setPendingAction('crear-plan');
    setLoading(true);
    try {
      const token = sesionSSO?.access_token || '';
      const plan = await apolloClient.registrarPlanSeguroGraphQL(nuevoPlanForm, token);
      setPlanes((prev) => [...prev, plan]);
      showToast('success', `Plan "${plan.nombre}" incorporado al catálogo corporativo.`);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  const handleAgregarCobertura = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pendingAction) return;
    setPendingAction('agregar-cobertura');
    setLoading(true);
    try {
      const token = sesionSSO?.access_token || '';
      await apolloClient.agregarCoberturaPlanGraphQL(nuevaCoberturaForm, token);
      const catalogoResp = await apolloClient.listarCatalogoYClientes(token);
      setPlanes(catalogoResp.planes);
      showToast('success', `Cobertura "${nuevaCoberturaForm.nombre}" añadida exitosamente al plan.`);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  const handleCrearCliente = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pendingAction) return;
    setPendingAction('crear-cliente');
    setLoading(true);
    try {
      const token = sesionSSO?.access_token || '';
      const cliente = await apolloClient.registrarClienteGraphQL(nuevoClienteForm, token);
      setClientesList((prev) => [cliente, ...prev]);
      setClienteActivoId(cliente.id);
      const resumenResp = await apolloClient.consultarResumenUnificadoAsegurado(cliente.id, token);
      sincronizarEstadoResumen(resumenResp.payload);
      showToast('success', `Asegurado "${cliente.nombreCompleto}" registrado y seleccionado como cliente activo.`);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  // =========================================================================
  // GESTIÓN Y ALTERNANCIA DE PLANES DE SEGURO (CATÁLOGO)
  // =========================================================================
  const handleToggleEstadoPlan = async (plan: PlanSeguro) => {
    if (pendingAction) return;
    const actionKey = `toggle-plan-${plan.id}`;
    setPendingAction(actionKey);
    try {
      await apolloClient.alternarEstadoPlan(plan.id);
      setPlanes((prev) =>
        prev.map((p) => (p.id === plan.id ? { ...p, activo: !p.activo } : p))
      );
      showToast(
        'success',
        `Plan "${plan.nombre}" ${plan.activo ? 'pausado' : 'activado'} en el catálogo.`
      );
    } catch {
      showToast('error', 'No se pudo alternar el estado del plan.');
    } finally {
      setPendingAction(null);
    }
  };

  const handleSeleccionarPlanParaCotizar = (plan: PlanSeguro) => {
    setCotizadorForm((prev) => ({
      ...prev,
      planId: plan.id,
      tipoPlan: plan.tipo
    }));
    setActiveTab('cotizador');
    showToast('success', `Plan "${plan.nombre}" seleccionado para cotización.`);
  };

  // =========================================================================
  // RESPALDO DE DOCUMENTOS RUAT/CI EN AMAZON S3
  // =========================================================================
  const handleRespaldarDocumentoS3 = async (customDataUrl?: string) => {
    const canvas = docCanvasRef.current;
    if (!canvas && !customDataUrl) return;
    const dataUrl = customDataUrl || (canvas ? canvas.toDataURL('image/png') : '');
    if (!dataUrl) return;
    const placaLimpia = (cotizadorForm.placa || 'DOCUMENTO').replace(/[^a-zA-Z0-9-]/g, '');
    const fileName = `RUAT-${placaLimpia}.png`;
    setPendingAction('subir-s3');
    try {
      const res = await apolloClient.subirDocumentoAS3(dataUrl, fileName, 'documentos-ruat');
      setDocumentoS3Info(res);
      showToast('success', `Documento respaldado en Amazon S3 (${res.key}).`);
      return res;
    } catch {
      showToast('warning', 'No se pudo sincronizar el archivo con el bucket de Amazon S3.');
    } finally {
      setPendingAction(null);
    }
  };

  // =========================================================================
  // CÁMARA WEB EN VIVO Y CAPTURA DE DOCUMENTOS
  // =========================================================================
  const handleIniciarCamaraWeb = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showToast('warning', 'Su navegador o dispositivo no soporta acceso a cámara web.');
        return;
      }
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
      });
      streamRef.current = stream;
      setCamaraActiva(true);
      showToast('success', 'Cámara web activada. Encuadre su RUAT o Cédula y presione "Capturar Foto".');
    } catch {
      showToast('warning', 'No se pudo iniciar la cámara web (permiso denegado o cámara no disponible).');
    }
  };

  const handleDetenerCamaraWeb = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCamaraActiva(false);
  };

  const handleCapturarFotoCamara = () => {
    const video = videoRef.current;
    const canvas = docCanvasRef.current;
    if (!video || !canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.filter = 'none';
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    handleDetenerCamaraWeb();

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const resultado = validadorIA.validarNitidez(imageData.data, canvas.width, canvas.height, {
      tipoDoc: 'Captura Cámara Web RUAT',
      placa: cotizadorForm.placa
    });
    setValidacionNitidez(resultado);
    setVistaMapaBordes(false);
    imagenOriginalBackupRef.current = imageData;

    handleRespaldarDocumentoS3(canvas.toDataURL('image/png'));

    if (resultado.esValidoTfJs) {
      showToast('success', `Captura de documento verificada con éxito (${Math.round(resultado.nitidezScore * 100)}%).`);
    } else {
      showToast('error', `Captura desenfocada (${Math.round(resultado.nitidezScore * 100)}%). Intente con mayor iluminación.`);
    }
  };

  // =========================================================================
  // PROCESAMIENTO DE ARCHIVO (FILE INPUT Y DRAG & DROP)
  // =========================================================================
  const procesarArchivoImagen = (file: File) => {
    if (!file.type.startsWith('image/')) {
      showToast('error', 'Por favor seleccione o arrastre un archivo de imagen válido (PNG, JPG, WEBP).');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const img = new Image();
      img.onload = () => {
        const canvas = docCanvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        ctx.filter = 'none';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const resultado = validadorIA.validarNitidez(imageData.data, canvas.width, canvas.height, {
          tipoDoc: file.name,
          placa: cotizadorForm.placa
        });
        setValidacionNitidez(resultado);
        setVistaMapaBordes(false);
        imagenOriginalBackupRef.current = imageData;
        handleRespaldarDocumentoS3(canvas.toDataURL('image/png'));
        if (resultado.esValidoTfJs) {
          showToast('success', `Documento "${file.name}" verificado y respaldado en S3.`);
        } else {
          showToast('error', `La imagen "${file.name}" no supera el umbral mínimo de nitidez.`);
        }
      };
      img.src = String(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // Escaneo Inteligente de Nitidez Documental y Emisión
  const handleSimularDocumento = (modo: 'NITIDA_HD' | 'BORROSA_DESENFOCADA') => {
    setModoEscaneoActual(modo);
    setVistaMapaBordes(false);
    imagenOriginalBackupRef.current = null;
    renderizarVistaPreviaDocumento(modo, cotizadorForm.placa, cotizadorForm.marca, cotizadorForm.modelo);

    const tensor = validadorIA.generarTensorSimulado(modo, 96, 64);
    const resultado = validadorIA.validarNitidez(tensor.pixels, tensor.width, tensor.height, {
      tipoDoc: 'Certificado RUAT + Cédula de Identidad',
      placa: cotizadorForm.placa
    });
    setValidacionNitidez(resultado);
    if (resultado.esValidoTfJs) {
      showToast('success', `Documento verificado con éxito (Calidad de imagen: ${Math.round(resultado.nitidezScore * 100)}%).`);
      if (docCanvasRef.current) {
        handleRespaldarDocumentoS3(docCanvasRef.current.toDataURL('image/png'));
      }
    } else {
      showToast('error', `Documento ilegible o desenfocado (${Math.round(resultado.nitidezScore * 100)}%). Capture una imagen más clara.`);
    }
  };

  const handleArchivoSubido = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      procesarArchivoImagen(file);
    }
  };

  // =========================================================================
  // MAPA DE DETECCIÓN DE BORDES IA DE ALTO CONTRASTE (#10B981 SOBRE #0F172A)
  // =========================================================================
  const handleAlternarMapaBordesIA = () => {
    const canvas = docCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (vistaMapaBordes) {
      if (imagenOriginalBackupRef.current) {
        ctx.putImageData(imagenOriginalBackupRef.current, 0, 0);
      } else {
        renderizarVistaPreviaDocumento(
          modoEscaneoActual,
          cotizadorForm.placa,
          cotizadorForm.marca,
          cotizadorForm.modelo
        );
      }
      setVistaMapaBordes(false);
      showToast('success', 'Vista normal del documento restaurada.');
      return;
    }

    const srcData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    imagenOriginalBackupRef.current = srcData;

    const width = canvas.width;
    const height = canvas.height;
    const src = srcData.data;
    const edgeData = ctx.createImageData(width, height);
    const dst = edgeData.data;

    const gray = new Float32Array(width * height);
    for (let i = 0; i < src.length; i += 4) {
      gray[i / 4] = 0.299 * src[i] + 0.587 * src[i + 1] + 0.114 * src[i + 2];
    }

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const gx =
          -1 * gray[(y - 1) * width + (x - 1)] +
          1 * gray[(y - 1) * width + (x + 1)] +
          -2 * gray[y * width + (x - 1)] +
          2 * gray[y * width + (x + 1)] +
          -1 * gray[(y + 1) * width + (x - 1)] +
          1 * gray[(y + 1) * width + (x + 1)];

        const gy =
          -1 * gray[(y - 1) * width + (x - 1)] +
          -2 * gray[(y - 1) * width + x] +
          -1 * gray[(y - 1) * width + (x + 1)] +
          1 * gray[(y + 1) * width + (x - 1)] +
          2 * gray[(y + 1) * width + x] +
          1 * gray[(y + 1) * width + (x + 1)];

        const mag = Math.sqrt(gx * gx + gy * gy);
        const pixelIdx = (y * width + x) * 4;

        if (mag > 40) {
          // Color esmeralda #10B981
          dst[pixelIdx] = 16;
          dst[pixelIdx + 1] = 185;
          dst[pixelIdx + 2] = 129;
          dst[pixelIdx + 3] = 255;
        } else {
          // Fondo oscuro #0F172A
          dst[pixelIdx] = 15;
          dst[pixelIdx + 1] = 23;
          dst[pixelIdx + 2] = 42;
          dst[pixelIdx + 3] = 255;
        }
      }
    }

    ctx.putImageData(edgeData, 0, 0);
    setVistaMapaBordes(true);
    showToast('success', 'Mapa de bordes IA generado: Resaltando contornos de alta frecuencia.');
  };

  // =========================================================================
  // INTEGRACIÓN WHATSAPP -> PASARELA QR
  // =========================================================================
  const handlePagarFacturaWhatsAppConQR = () => {
    if (!pedidoWhatsAppResult) return;
    setQrForm((prev) => ({
      ...prev,
      polizaId: pedidoWhatsAppResult.poliza.id,
      facturaId: pedidoWhatsAppResult.factura.id,
      monto: pedidoWhatsAppResult.factura.total,
      numeroCuota: 1
    }));
    setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
    showToast('success', `Factura ${pedidoWhatsAppResult.factura.numeroFactura} cargada en la Pasarela Bancaria QR.`);
    if (pasarelaQrSectionRef.current) {
      pasarelaQrSectionRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleCotizarPoliza = async () => {
    if (pendingAction) return;
    setPendingAction('cotizar');
    setLoading(true);
    try {
      const cot = await apolloClient.cotizarPolizaEnLinea(
        {
          tipoPlan: cotizadorForm.tipoPlan,
          planId: cotizadorForm.planId,
          edadConductor: cotizadorForm.edadConductor,
          ciudad: cotizadorForm.ciudad,
          datosBien: {
            placa: cotizadorForm.placa,
            vin: cotizadorForm.vin,
            marca: cotizadorForm.marca,
            modelo: cotizadorForm.modelo,
            anio: cotizadorForm.anio,
            color: cotizadorForm.color,
            valorComercial: cotizadorForm.valorComercial
          }
        },
        sesionSSO?.access_token || ''
      );
      setCotizacionActual(cot);
      showToast('success', `Cotización lista: USD ${cot.primaCalculadaAnual.toLocaleString()} anuales (USD ${cot.primaCalculadaMensual}/mes).`);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  const handleEmitirPoliza = async () => {
    if (pendingAction) return;
    if (!validacionNitidez || !validacionNitidez.esValidoTfJs) {
      showToast('error', 'Por favor verifique que el documento adjunto sea nítido antes de emitir la póliza.');
      return;
    }

    setPendingAction('emitir-poliza');
    setLoading(true);
    try {
      const token = sesionSSO?.access_token || '';
      const res = await apolloClient.emitirPolizaEnLinea(
        {
          clienteId: clienteActivoId,
          planId: cotizadorForm.planId,
          datosBien: {
            placa: cotizadorForm.placa,
            vin: cotizadorForm.vin,
            marca: cotizadorForm.marca,
            modelo: cotizadorForm.modelo,
            anio: cotizadorForm.anio,
            color: cotizadorForm.color,
            valorComercial: cotizadorForm.valorComercial
          },
          fechaInicio: new Date().toISOString().slice(0, 10),
          mesesVigencia: 12,
          canalVenta: 'WEB_REACT',
          tokenValidacionNitidezLocal: validacionNitidez.tokenValidacionNitidezLocal
        },
        isOffline,
        token
      );

      if (res.encoladoOffline) {
        setColaOffline(apolloClient.obtenerColaOffline());
        showToast('warning', 'Solicitud guardada en modo sin conexión. Se emitirá automáticamente al recuperar red.');
      } else if (res.poliza) {
        setPolizaRecienEmitida(res.poliza);
        if (!documentoS3Info && docCanvasRef.current) {
          handleRespaldarDocumentoS3(docCanvasRef.current.toDataURL('image/png')).catch(() => {});
        }
        const resumenResp = await apolloClient.consultarResumenUnificadoAsegurado(clienteActivoId, token);
        sincronizarEstadoResumen(resumenResp.payload);
        showToast('success', `¡Felicidades! Póliza ${res.poliza.numeroPoliza} emitida y activada.`);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'No se pudo completar la emisión';
      showToast('error', msg);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  // Emisión Express vía WhatsApp + Factura PDF
  const handleContratacionWhatsApp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pendingAction) return;
    setPendingAction('whatsapp-n8n');
    setLoading(true);
    try {
      const res = await apolloClient.contratarPolizaWhatsAppN8n(whatsappForm);
      setPedidoWhatsAppResult(res);
      setQrForm((prev) => ({
        ...prev,
        polizaId: res.poliza.id,
        facturaId: res.factura.id,
        monto: res.factura.total
      }));
      setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
      const token = sesionSSO?.access_token || '';
      const resumenResp = await apolloClient.consultarResumenUnificadoAsegurado(clienteActivoId, token);
      sincronizarEstadoResumen(resumenResp.payload);
      showToast('success', `Póliza ${res.poliza.numeroPoliza} y Factura ${res.factura.numeroFactura} generadas.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error al procesar contratación WhatsApp';
      showToast('error', msg);
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  // Pago por QR Sandbox Funcional con Persistencia Real en PostgreSQL y DynamoDB
  const handleEjecutarPagoQR = async (reusarMismaLlave: boolean) => {
    if (pendingAction) return;
    setPendingAction(reusarMismaLlave ? 'qr-retry' : 'qr-pay');
    setLoading(true);
    try {
      const keyToUse = reusarMismaLlave ? qrKeyUuid : ApolloFederationClient.generarUUIDv4();
      if (!reusarMismaLlave) {
        setQrKeyUuid(keyToUse);
      }

      const res = await apolloClient.procesarPagoPrimaQRIdempotente(
        {
          polizaId: qrForm.polizaId,
          facturaId: qrForm.facturaId || undefined,
          numeroCuota: qrForm.numeroCuota,
          monto: qrForm.monto,
          bancoSandbox: qrForm.bancoSandbox
        },
        keyToUse
      );
      setQrPagoResult(res);
      const pagosQrResp = await apolloClient.listarPagosQrRegistrados();
      setHistorialPagosQr(pagosQrResp);
      if (res.fueIdempotente) {
        showToast('warning', 'Protección contra doble cobro activada: La transacción ya fue procesada anteriormente.');
      } else {
        showToast('success', `Pago QR procesado y guardado en base de datos (${res.codigoAutorizacion}).`);
      }
    } catch {
      showToast('error', 'No se pudo conectar con la pasarela de pagos QR.');
    } finally {
      setLoading(false);
      setPendingAction(null);
    }
  };

  // Matriz determinística para que el código QR visual cambie dinámicamente con los datos de la orden
  const qrCells = useMemo(() => {
    const seedStr = `${qrForm.polizaId}|${qrForm.monto}|${qrForm.numeroCuota}|${qrForm.bancoSandbox}|${qrKeyUuid}`;
    let hash = 2166136261;
    for (let i = 0; i < seedStr.length; i++) {
      hash ^= seedStr.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    const cells: Array<{ x: number; y: number }> = [];
    for (let row = 0; row < 11; row++) {
      for (let col = 0; col < 11; col++) {
        // Excluir las 3 esquinas de posicionamiento del QR
        const inTopLeft = row < 4 && col < 4;
        const inTopRight = row < 4 && col > 6;
        const inBottomLeft = row > 6 && col < 4;
        const inCenterLogo = row >= 4 && row <= 6 && col >= 4 && col <= 6;
        if (inTopLeft || inTopRight || inBottomLeft || inCenterLogo) continue;

        const bit = ((hash >>> ((row * 11 + col) % 28)) ^ (row * 7 + col * 13)) & 1;
        if (bit === 1) {
          cells.push({ x: 10 + col * 7.2, y: 10 + row * 7.2 });
        }
      }
    }
    return cells;
  }, [qrForm.bancoSandbox, qrForm.monto, qrForm.numeroCuota, qrForm.polizaId, qrKeyUuid]);

  const polizaPrincipal = resumenUnificado?.polizasActivas[0] || null;
  const techoReferencia = 25000;
  const porcentajeDisponible = polizaPrincipal
    ? Math.min(100, Math.max(5, Math.round((polizaPrincipal.saldoCoberturaRestante / techoReferencia) * 100)))
    : 100;

  // Verificación en progreso
  if (!authChecked) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex flex-col items-center justify-center gap-3">
        <div className="w-10 h-10 border-3 border-teal-200 border-t-[#005C55] rounded-full animate-spin" />
        <p className="text-xs font-mono text-slate-600 font-semibold">Verificando sesión OIDC en DynamoDB...</p>
      </div>
    );
  }

  // Guardia de Autenticación OIDC Estricta (Requerimiento 3)
  if (!sesionSSO) {
    return (
      <div className="min-h-screen bg-[#070E1A] text-slate-100 flex flex-col justify-between selection:bg-[#005C55]/30">
        <header className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#005C55] to-[#0F766E] text-white flex items-center justify-center shadow-lg border border-teal-400/20">
              <span className="material-symbols-outlined text-[22px]">shield_lock</span>
            </div>
            <div>
              <span className="font-headline font-bold text-sm tracking-tight text-white block">
                AegisCore <span className="text-teal-400">Portal Asegurados</span>
              </span>
              <span className="text-[10px] font-mono text-slate-400">Autenticación Requerida · OIDC PKCE S256</span>
            </div>
          </div>
          <a
            href={obtenerSsoHubUrl()}
            className="text-xs font-mono text-teal-300 hover:text-teal-200 bg-white/5 border border-white/10 px-3.5 py-1.5 rounded-full flex items-center gap-1.5 transition-all"
          >
            <span className="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>Bóveda Central</span>
          </a>
        </header>

        <div className="flex-1 flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-slate-900/90 border border-white/15 rounded-3xl p-8 text-center space-y-6 shadow-2xl backdrop-blur-xl">
            <div className="w-16 h-16 rounded-2xl bg-teal-950/70 border border-teal-500/30 text-teal-400 mx-auto flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-3xl">lock</span>
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-teal-400 font-semibold">
                Control de Acceso Centralizado
              </span>
              <h2 className="text-2xl font-bold font-headline text-white mt-1">
                Autenticación Corporativa Requerida
              </h2>
              <p className="text-xs text-slate-300 mt-2.5 leading-relaxed">
                No se detectó una sesión activa en la Bóveda de Identidad OIDC. Para acceder a sus pólizas, certificados y pasarela de pago, debe autenticarse en el Workspace Hub corporativo.
              </p>
            </div>
            <div className="pt-2">
              <a
                href={obtenerSsoHubUrl()}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-[#005C55] to-[#0F766E] text-white text-xs font-bold font-headline tracking-wide hover:brightness-110 active:scale-[0.99] transition-all flex items-center justify-center gap-2 shadow-lg shadow-teal-950/60"
              >
                <span className="material-symbols-outlined text-[18px]">login</span>
                <span>Iniciar Sesión en Portal Central SSO</span>
              </a>
            </div>
            <p className="text-[11px] font-mono text-slate-500">
              Redirigiendo automáticamente a la Bóveda Central...
            </p>
          </div>
        </div>

        <footer className="py-4 text-center text-xs text-slate-500 border-t border-white/5 font-mono">
          © 2026 AegisCore AI Seguros — OIDC PKCE S256 & DynamoDB Idempotency
        </footer>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F8FAFC] text-[#0F172A]">
      {/* BARRA SUPERIOR PERSISTENTE: RETORNO AL PORTAL CENTRAL SSO (MISMA PESTAÑA) */}
      <div className="bg-[#0B1C30] text-slate-200 px-4 py-2 text-xs flex items-center justify-between border-b border-white/10 z-50 shadow-sm">
        <div className="flex items-center gap-2.5">
          <button
            type="button"
            onClick={volverAlHubCentral}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-400/40 text-xs font-bold transition-all shadow-2xs cursor-pointer"
            title="Volver al Portal Central SSO sin abrir pestañas nuevas"
          >
            <span className="material-symbols-outlined text-[16px]">arrow_back</span>
            <span>← Volver al Portal Central SSO</span>
          </button>
          <span className="text-slate-500 hidden sm:inline">|</span>
          <span className="text-slate-400 text-[11px] font-mono hidden sm:inline">
            AegisCore Tri-Cloud · Navegación en una sola pestaña
          </span>
        </div>
        <div className="flex items-center gap-2 text-[11px] font-mono text-teal-400">
          <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse"></span>
          <span>Sesión OIDC: {sesionSSO.email}</span>
        </div>
      </div>
      {/* HEADER CORPORATIVO LIMPIO Y MODERNO */}
      <header className="bg-white/90 backdrop-blur-xl border-b border-slate-200/80 sticky top-0 z-40 shadow-[0_1px_6px_rgba(15,23,42,0.03)] relative">
        {(loading || pendingAction !== null) && (
          <div className="absolute top-0 left-0 right-0 h-1 bg-teal-100 overflow-hidden z-50">
            <div className="h-full w-1/2 bg-gradient-to-r from-[#005C55] via-teal-400 to-[#005C55] animate-pulse" />
          </div>
        )}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between gap-4">
          {/* Identidad de Marca */}
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-[#005C55] to-[#0F766E] flex items-center justify-center text-white shadow-sm">
              <span className="material-symbols-outlined text-[24px]">shield_with_heart</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-heading text-xl font-extrabold tracking-tight text-slate-900">
                  AegisCore
                </span>
                <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-teal-50 text-[#005C55] border border-teal-200/80">
                  Seguros &amp; Patrimonio
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Gestión digital de pólizas, suscripción en línea y cobertura en tiempo real
              </p>
            </div>
          </div>

          {/* Controles Superiores: Selector de Cliente (RBAC) + Estado de Red + Perfil + Logout */}
          <div className="flex flex-wrap items-center gap-2.5">
            {sesionSSO.rol === 'CLIENTE' ? (
              <div className="flex items-center gap-2 border rounded-full px-3.5 py-1.5 bg-teal-50/90 border-teal-200 text-teal-950 shadow-2xs">
                <span className="material-symbols-outlined text-[16px] text-[#005C55]">badge</span>
                <span className="text-xs font-bold font-headline">{sesionSSO.nombre_completo}</span>
                <span className="text-[10px] font-mono font-bold bg-[#005C55] text-white px-2 py-0.5 rounded-full">
                  Asegurado Titular
                </span>
              </div>
            ) : (
              clientesList.length > 0 && (
                <div
                  className={`flex items-center gap-2 border rounded-full px-3 py-1.5 transition-all ${
                    pendingAction === 'switch-client'
                      ? 'bg-teal-50 border-teal-300 ring-2 ring-teal-500/20'
                      : 'bg-slate-100/90 border-slate-200/90 hover:border-teal-300'
                  }`}
                >
                  <span
                    className={`material-symbols-outlined text-[16px] text-[#005C55] ${
                      pendingAction === 'switch-client' ? 'animate-spin' : ''
                    }`}
                  >
                    {pendingAction === 'switch-client' ? 'progress_activity' : 'person'}
                  </span>
                  <select
                    value={clienteActivoId}
                    disabled={pendingAction === 'switch-client'}
                    onChange={(e) => handleSelectClienteActivo(e.target.value)}
                    className="bg-transparent text-xs font-semibold text-slate-800 focus:outline-none cursor-pointer disabled:opacity-60"
                    title="Cambiar asegurado activo"
                  >
                    {clientesList.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.nombreCompleto} ({c.numeroDocumento})
                      </option>
                    ))}
                  </select>
                  {pendingAction === 'switch-client' && (
                    <span className="text-[10px] font-bold text-[#005C55] animate-pulse">
                      Cargando...
                    </span>
                  )}
                </div>
              )
            )}

            <button
              type="button"
              onClick={handleToggleOffline}
              className={`inline-flex items-center gap-1.5 px-3.5 py-2 rounded-full text-xs font-semibold transition-all border ${
                isOffline
                  ? 'bg-amber-50 border-amber-300 text-amber-900 shadow-xs'
                  : 'bg-emerald-50/80 border-emerald-200 text-emerald-800 hover:bg-emerald-100/70'
              }`}
              title="Detecta automáticamente caídas de Internet o permite simular modo sin conexión"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  isOffline ? 'bg-amber-500 animate-ping' : 'bg-emerald-500'
                }`}
              />
              <span className="material-symbols-outlined text-[16px]">
                {isOffline ? 'cloud_off' : 'cloud_done'}
              </span>
              <span>
                {isOffline
                  ? `Sin conexión${colaOffline.filter((i) => i.estado === 'PENDIENTE_RED').length > 0 ? ` (${colaOffline.filter((i) => i.estado === 'PENDIENTE_RED').length} en cola)` : ''}`
                  : 'En línea'}
              </span>
            </button>

            <button
              type="button"
              onClick={volverAlHubCentral}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#005C55] hover:bg-[#0F766E] text-white text-xs font-bold transition-all shadow-sm cursor-pointer"
              title="Volver a la Bóveda Central SSO (Selector de Módulos)"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Bóveda Central</span>
            </button>

            <button
              type="button"
              onClick={() => handleCerrarSesionSSO('ALL')}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-semibold transition-all shadow-2xs"
              title="Cerrar sesión corporativa en todos los microservicios"
            >
              <span className="material-symbols-outlined text-[16px]">logout</span>
              <span className="hidden sm:inline">Cerrar Sesión</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('seguridad')}
              className="flex items-center gap-2.5 pl-2 pr-3.5 py-1.5 rounded-full bg-slate-100 hover:bg-slate-200/70 border border-slate-200/90 transition-colors"
            >
              <div className="w-7 h-7 rounded-full bg-[#0F172A] text-white flex items-center justify-center text-xs font-bold">
                {sesionSSO.nombre_completo.slice(0, 1)}
              </div>
              <div className="text-left hidden md:block">
                <p className="text-xs font-semibold text-slate-900 leading-none">
                  {sesionSSO.nombre_completo}
                </p>
                <p className="text-[10px] font-medium text-slate-500 mt-0.5">
                  {sesionSSO.rol === 'CLIENTE' ? 'Asegurado Titular' : sesionSSO.rol}
                </p>
              </div>
            </button>
          </div>
        </div>

        {/* BARRA DE NAVEGACIÓN PRINCIPAL (FILTRADA POR RBAC) */}
        <div className="border-t border-slate-200/60 bg-slate-50/70">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 flex overflow-x-auto no-scrollbar gap-1.5 py-2">
            {tabsDisponibles.map((tab) => {
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveTab(tab.id as ActiveTab)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                    active
                      ? 'bg-[#005C55] text-white shadow-sm'
                      : 'text-slate-600 hover:bg-white hover:text-slate-900'
                  }`}
                >
                  <span className="material-symbols-outlined text-[18px]">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* BANNER AUTOMÁTICO CUANDO SE DETECTA CORTE DE INTERNET O HAY OPERACIONES EN COLA */}
      {(isOffline || colaOffline.some((i) => i.estado === 'PENDIENTE_RED')) && (
        <div className="bg-amber-50 border-b border-amber-200/90 px-4 sm:px-6 py-2.5">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2 text-xs text-amber-900">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[18px] text-amber-700">wifi_off</span>
              <span>
                {isOffline
                  ? 'Se encuentra operando sin conexión a Internet. Puede seguir cotizando y emitiendo pólizas; se sincronizarán automáticamente al volver en línea.'
                  : `Tiene ${colaOffline.filter((i) => i.estado === 'PENDIENTE_RED').length} operación(es) pendiente(s) de sincronización.`}
              </span>
            </div>
            {colaOffline.some((i) => i.estado === 'PENDIENTE_RED') && (
              <button
                type="button"
                onClick={async () => {
                  const act = await apolloClient.sincronizarColaOffline(sesionSSO.access_token);
                  setColaOffline(act);
                  showToast('success', 'Cola de operaciones sincronizada exitosamente.');
                  await cargarDatosIniciales();
                }}
                className="px-3 py-1 rounded-lg bg-amber-800 text-white font-semibold hover:bg-amber-900"
              >
                Sincronizar Ahora
              </button>
            )}
          </div>
        </div>
      )}

      {/* NOTIFICACIÓN FLOTANTE */}
      {toastMessage && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 mt-4 w-full">
          <div
            className={`flex items-center justify-between px-4 py-3 rounded-xl border text-xs sm:text-sm font-medium shadow-sm transition-all ${
              toastMessage.type === 'success'
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : toastMessage.type === 'warning'
                ? 'bg-amber-50 border-amber-200 text-amber-900'
                : 'bg-red-50 border-red-200 text-red-900'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="material-symbols-outlined text-[20px]">
                {toastMessage.type === 'success'
                  ? 'check_circle'
                  : toastMessage.type === 'warning'
                  ? 'warning'
                  : 'error'}
              </span>
              <span>{toastMessage.text}</span>
            </div>
            <button
              type="button"
              onClick={() => setToastMessage(null)}
              className="text-xs font-semibold opacity-70 hover:opacity-100 ml-4"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* CONTENIDO PRINCIPAL */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* =====================================================================
             SECCIÓN 1: MI PÓLIZA Y COBERTURA
        ===================================================================== */}
        {activeTab === 'resumen' && resumenUnificado && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h1 className="font-heading text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
                  Hola, {resumenUnificado.cliente.nombres}
                </h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Consulte el estado actualizado de sus pólizas, vehículos asegurados y asistencias en curso.
                </p>
              </div>
              <div className="flex items-center gap-2.5">
                <button
                  type="button"
                  onClick={() => setActiveTab('cotizador')}
                  className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#005C55] text-white text-xs font-semibold hover:bg-[#0F766E] transition-colors shadow-sm"
                >
                  <span className="material-symbols-outlined text-[18px]">add_circle</span>
                  <span>Nueva Cotización</span>
                </button>
                <button
                  type="button"
                  onClick={() => cargarDatosIniciales()}
                  disabled={loading}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors"
                >
                  <span className={`material-symbols-outlined text-[18px] ${loading ? 'animate-spin' : ''}`}>
                    refresh
                  </span>
                  <span>Actualizar</span>
                </button>
              </div>
            </div>

            {/* Tarjetas de Métricas Ejecutivas */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-sm flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">Cobertura Disponible</span>
                  <span className="w-8 h-8 rounded-lg bg-teal-50 text-[#005C55] flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">account_balance_wallet</span>
                  </span>
                </div>
                <div className="mt-3">
                  <p className="font-mono text-2xl font-bold text-[#005C55]">
                    USD {resumenUnificado.totalSaldoCoberturaDisponible.toLocaleString()}
                  </p>
                  <div className="w-full bg-slate-100 h-1.5 rounded-full mt-2.5 overflow-hidden">
                    <div
                      className="bg-[#005C55] h-full rounded-full transition-all duration-500"
                      style={{ width: `${porcentajeDisponible}%` }}
                    />
                  </div>
                </div>
                <span className="text-[11px] text-slate-500 mt-2">
                  Respaldo patrimonial activo ({porcentajeDisponible}%)
                </span>
              </div>

              <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-sm flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">Prima Anual Vigente</span>
                  <span className="w-8 h-8 rounded-lg bg-slate-100 text-slate-700 flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">receipt_long</span>
                  </span>
                </div>
                <div className="mt-3">
                  <p className="font-mono text-2xl font-bold text-slate-900">
                    USD {polizaPrincipal ? polizaPrincipal.primaAnual.toLocaleString() : '0'}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Cuota mensual: <strong className="font-mono text-slate-700">USD {polizaPrincipal?.primaMensual || 60}</strong>
                  </p>
                </div>
                <span className="text-[11px] text-emerald-700 font-semibold mt-2">
                  ● {resumenUnificado.pagosPendientes.some((f) => f.estado === 'EMITIDA') ? 'Facturas disponibles para pago QR' : 'Pagos al día'}
                </span>
              </div>

              <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-sm flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">Calificación de Conductor</span>
                  <span className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">workspace_premium</span>
                  </span>
                </div>
                <div className="mt-3">
                  <p className="font-mono text-2xl font-bold text-slate-900">
                    {resumenUnificado.cliente.scoreCrediticio || 820} <span className="text-xs font-normal text-slate-400">/ 900</span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Documento: <span className="font-mono">{resumenUnificado.cliente.numeroDocumento}</span>
                  </p>
                </div>
                <span className="text-[11px] text-emerald-700 font-semibold mt-2">
                  Nivel de Riesgo {resumenUnificado.cliente.perfilRiesgo || 'Bajo'} (Bonificación activa)
                </span>
              </div>

              <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-sm flex flex-col justify-between">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-500">Asistencias y Reclamos</span>
                  <span className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">car_crash</span>
                  </span>
                </div>
                <div className="mt-3">
                  <p className="font-mono text-2xl font-bold text-slate-900">
                    {resumenUnificado.siniestrosEnCurso.length}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Expedientes en seguimiento
                  </p>
                </div>
                <span className="text-[11px] text-indigo-600 font-semibold mt-2">
                  Peritaje digital asistido
                </span>
              </div>
            </div>

            {/* Buscador Rápido de Pólizas, Placas y Siniestros */}
            <div className="bg-white rounded-2xl border border-slate-200/90 p-3.5 shadow-sm flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2.5 flex-1 min-w-[240px]">
                <span className="material-symbols-outlined text-slate-400 text-[20px] ml-1">search</span>
                <input
                  type="text"
                  value={filtroBusquedaResumen}
                  onChange={(e) => setFiltroBusquedaResumen(e.target.value)}
                  placeholder="Buscar por placa (ej. 4028-PLK), número de póliza, marca o expediente..."
                  className="w-full text-xs text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
                />
                {filtroBusquedaResumen && (
                  <button
                    type="button"
                    onClick={() => setFiltroBusquedaResumen('')}
                    className="text-xs text-slate-400 hover:text-slate-600 px-2"
                  >
                    Limpiar
                  </button>
                )}
              </div>
              <div className="flex items-center gap-2 text-[11px] text-slate-500 px-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium">
                  <span className="material-symbols-outlined text-[14px] text-[#005C55]">bolt</span>
                  <span>Respuesta instantánea ({resumenUnificado.cacheDynamoDb?.latency_ms ?? 1.4} ms)</span>
                </span>
              </div>
            </div>

            {/* Detalle de Pólizas Activas y Seguimiento de Siniestros */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Columna Izquierda: Pólizas y Vehículos */}
              <div className="lg:col-span-7 space-y-4">
                <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="material-symbols-outlined text-[#005C55]">directions_car</span>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Mis Pólizas y Vehículos Asegurados
                      </h2>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-teal-50 text-[#005C55]">
                      {resumenUnificado.polizasActivas.length} Activa(s)
                    </span>
                  </div>

                  <div className="p-6 space-y-5">
                    {resumenUnificado.polizasActivas
                      .filter((pol) => {
                        if (!filtroBusquedaResumen.trim()) return true;
                        const q = filtroBusquedaResumen.toLowerCase();
                        return (
                          pol.numeroPoliza.toLowerCase().includes(q) ||
                          pol.bienAsegurado.placa.toLowerCase().includes(q) ||
                          pol.bienAsegurado.marca.toLowerCase().includes(q) ||
                          pol.bienAsegurado.modelo.toLowerCase().includes(q) ||
                          (pol.plan?.nombre || '').toLowerCase().includes(q)
                        );
                      })
                      .map((pol: Poliza) => {
                        const montoPoliza = montosAjustePorPoliza[pol.id] ?? 3200;
                        const expandida = Boolean(coberturasExpandidasPorPoliza[pol.id]);
                        const certS3 = certificadosS3PorPoliza[pol.id];
                        const isCertLoading = pendingAction === `cert-${pol.id}`;
                        const coberturasPlan =
                          pol.plan?.coberturas && pol.plan.coberturas.length > 0
                            ? pol.plan.coberturas
                            : planes.find((p) => p.id === pol.plan?.id)?.coberturas || [];

                        return (
                          <div
                            key={pol.id}
                            className="rounded-2xl border border-slate-200/90 p-5 bg-slate-50/40 hover:bg-white hover:shadow-sm transition-all space-y-4"
                          >
                            <div className="flex flex-wrap items-start justify-between gap-3">
                              <div>
                                <div className="flex flex-wrap items-center gap-2">
                                  <span className="font-mono text-sm font-bold text-slate-900">
                                    {pol.numeroPoliza}
                                  </span>
                                  <span className="px-2.5 py-0.5 text-[11px] font-semibold rounded-full bg-emerald-100 text-emerald-800">
                                    {pol.estado}
                                  </span>
                                  {pol.plan?.nombre && (
                                    <span className="px-2.5 py-0.5 text-[11px] font-medium rounded-full bg-slate-100 text-slate-700">
                                      {pol.plan.nombre}
                                    </span>
                                  )}
                                </div>
                                <h3 className="font-heading text-base font-bold text-slate-900 mt-1.5">
                                  {pol.bienAsegurado.marca} {pol.bienAsegurado.modelo} ({pol.bienAsegurado.anio})
                                </h3>
                                <p className="text-xs text-slate-500 mt-0.5">
                                  Placa: <strong className="font-mono text-slate-700">{pol.bienAsegurado.placa}</strong> · VIN:{' '}
                                  <span className="font-mono text-slate-600">{pol.bienAsegurado.vin}</span> · Valor:{' '}
                                  <strong className="font-mono text-slate-700">
                                    USD {pol.bienAsegurado.valorComercial.toLocaleString()}
                                  </strong>
                                </p>
                              </div>

                              <div className="text-right">
                                <span className="text-[11px] text-slate-400 uppercase font-semibold tracking-wider block">
                                  Cobertura Restante
                                </span>
                                <span className="font-mono text-lg font-bold text-[#005C55]">
                                  USD {pol.saldoCoberturaRestante.toLocaleString()}
                                </span>
                                <span className="text-[11px] text-slate-500 block">
                                  Vigencia hasta {pol.fechaFin.slice(0, 10)}
                                </span>
                              </div>
                            </div>

                            {/* Acciones de Póliza: Ver Coberturas y Descargar Certificado PDF en Amazon S3 */}
                            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-200/60">
                              <button
                                type="button"
                                onClick={() =>
                                  setCoberturasExpandidasPorPoliza((prev) => ({
                                    ...prev,
                                    [pol.id]: !prev[pol.id]
                                  }))
                                }
                                className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#005C55] hover:underline"
                              >
                                <span className="material-symbols-outlined text-[16px]">
                                  {expandida ? 'expand_less' : 'expand_more'}
                                </span>
                                <span>
                                  {expandida
                                    ? 'Ocultar coberturas y deducibles'
                                    : `Ver coberturas incluidas (${coberturasPlan.length || 3})`}
                                </span>
                              </button>

                              <div className="flex flex-wrap items-center gap-2">
                                <button
                                  type="button"
                                  disabled={pendingAction !== null}
                                  onClick={() => handleDescargarCertificadoPolizaS3(pol.id, pol.numeroPoliza)}
                                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-50 border border-teal-200 text-[#005C55] text-xs font-semibold hover:bg-teal-100/80 active:scale-[0.98] disabled:opacity-60 transition-all"
                                >
                                  <span
                                    className={`material-symbols-outlined text-[15px] ${
                                      isCertLoading ? 'animate-spin' : ''
                                    }`}
                                  >
                                    {isCertLoading ? 'progress_activity' : 'cloud_download'}
                                  </span>
                                  <span>
                                    {isCertLoading ? 'Subiendo a S3...' : 'Certificado PDF (Amazon S3)'}
                                  </span>
                                </button>
                              </div>
                            </div>

                            {certS3?.s3Url && (
                              <div className="px-3 py-2 rounded-xl bg-emerald-50/90 border border-emerald-200 flex flex-wrap items-center justify-between gap-2 text-[11px] text-emerald-900">
                                <span className="flex items-center gap-1.5 font-medium">
                                  <span className="material-symbols-outlined text-[15px] text-emerald-700">
                                    cloud_done
                                  </span>
                                  <span>Almacenado en Amazon S3 (`servicio-de-seguros-aegiscore`)</span>
                                </span>
                                <a
                                  href={certS3.s3Url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="font-mono font-bold text-[#005C55] underline"
                                >
                                  Abrir enlace directo S3
                                </a>
                              </div>
                            )}

                            {/* Tabla Desplegable de Coberturas y Deducibles */}
                            {expandida && (
                              <div className="rounded-xl bg-white border border-slate-200/80 p-3.5 space-y-2">
                                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                                  Desglose de Coberturas Contractuales
                                </p>
                                {coberturasPlan.length > 0 ? (
                                  <div className="divide-y divide-slate-100 text-xs">
                                    {coberturasPlan.map((cob) => (
                                      <div key={cob.id} className="py-2 flex items-center justify-between gap-2">
                                        <div>
                                          <p className="font-semibold text-slate-800">{cob.nombre}</p>
                                          <p className="text-[11px] text-slate-500">
                                            Deducible: {cob.deduciblePorcentaje}% (Mínimo USD {cob.deducibleMinimo})
                                          </p>
                                        </div>
                                        <span className="font-mono font-bold text-[#005C55]">
                                          Hasta USD {cob.sumaAseguradaMax.toLocaleString()}
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                ) : (
                                  <p className="text-xs text-slate-500">
                                    Cobertura Todo Riesgo (Daños Propios, Robo Total y Responsabilidad Civil Extracontractual).
                                  </p>
                                )}
                              </div>
                            )}

                            {/* Simulador de liquidación administrativo (Exclusivo para ADMIN y ACTUARIO) */}
                            {(sesionSSO.rol === 'ADMIN' || sesionSSO.rol === 'ACTUARIO') && (
                              <div className="pt-3 border-t border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-medium text-slate-600">
                                    Simular liquidación sobre cobertura (USD):
                                  </span>
                                  <input
                                    type="number"
                                    min={0}
                                    value={montoPoliza}
                                    onChange={(e) => {
                                      const val = Number(e.target.value);
                                      setMontosAjustePorPoliza((prev) => ({
                                        ...prev,
                                        [pol.id]: val
                                      }));
                                    }}
                                    className="w-24 px-2.5 py-1.5 text-xs font-mono bg-white border border-slate-300 rounded-lg focus:outline-none focus:border-[#005C55]"
                                  />
                                </div>
                                <div className="flex items-center gap-2">
                                  <button
                                    type="button"
                                    disabled={pendingAction !== null}
                                    onClick={() => handleAjusteCobertura('descontar-cobertura', pol.id)}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-600 text-white text-xs font-semibold hover:bg-amber-700 active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all"
                                  >
                                    {pendingAction === `descontar-cobertura-${pol.id}` && (
                                      <span className="material-symbols-outlined text-[14px] animate-spin">
                                        progress_activity
                                      </span>
                                    )}
                                    <span>
                                      {pendingAction === `descontar-cobertura-${pol.id}`
                                        ? 'Aplicando...'
                                        : 'Aplicar Descuento'}
                                    </span>
                                  </button>
                                  <button
                                    type="button"
                                    disabled={pendingAction !== null}
                                    onClick={() => handleAjusteCobertura('compensar-cobertura', pol.id)}
                                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-white text-xs font-semibold hover:bg-slate-900 active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all"
                                  >
                                    {pendingAction === `compensar-cobertura-${pol.id}` && (
                                      <span className="material-symbols-outlined text-[14px] animate-spin">
                                        progress_activity
                                      </span>
                                    )}
                                    <span>
                                      {pendingAction === `compensar-cobertura-${pol.id}`
                                        ? 'Restituyendo...'
                                        : 'Restituir Saldo'}
                                    </span>
                                  </button>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                </div>
              </div>

              {/* Columna Derecha: Seguimiento de Siniestros (con Evidencia S3) y Facturas del Asegurado */}
              <div className="lg:col-span-5 space-y-5">
                <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="material-symbols-outlined text-indigo-600">health_and_safety</span>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Seguimiento de Siniestros y Peritaje
                      </h2>
                    </div>
                    <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700">
                      Tiempo Real
                    </span>
                  </div>

                  <div className="p-6 space-y-4">
                    {resumenUnificado.siniestrosEnCurso.length === 0 ? (
                      <p className="text-xs text-slate-500 text-center py-4">
                        No registra siniestros activos en este momento.
                      </p>
                    ) : (
                      resumenUnificado.siniestrosEnCurso.map((sin) => {
                        const evidenciaUrl =
                          sin.fotosEvidencia?.[0]?.url ||
                          'https://servicio-de-seguros-aegiscore.s3.us-east-2.amazonaws.com/evidencias-siniestros/SIN-2026-0001-peritaje-frontal.svg';
                        return (
                          <div
                            key={sin.id}
                            className="p-4 rounded-2xl border border-slate-200/90 bg-slate-50/50 space-y-3"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <span className="font-mono text-xs font-bold text-slate-900">
                                  Expediente {sin.numeroReclamo}
                                </span>
                                <span className="text-[11px] text-slate-400 font-mono ml-2">
                                  ({sin.numeroPoliza})
                                </span>
                              </div>
                              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-900">
                                {sin.estado.replace(/_/g, ' ')}
                              </span>
                            </div>

                            <p className="text-xs text-slate-600 leading-relaxed">
                              {sin.descripcion || 'Inspección y evaluación técnica en curso.'}
                            </p>

                            {sin.ubicacionTexto && (
                              <p className="text-[11px] text-slate-500 flex items-center gap-1">
                                <span className="material-symbols-outlined text-[14px] text-[#005C55]">
                                  location_on
                                </span>
                                <span>{sin.ubicacionTexto}</span>
                              </p>
                            )}

                            {/* Piezas Evaluadas y Perito Asignado */}
                            {sin.triajeIa?.piezasDetectadas && sin.triajeIa.piezasDetectadas.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 pt-1">
                                {sin.triajeIa.piezasDetectadas.map((pieza) => (
                                  <span
                                    key={pieza}
                                    className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200/70 font-mono text-[10px] font-semibold"
                                  >
                                    {pieza.replace(/_/g, ' ')}
                                  </span>
                                ))}
                              </div>
                            )}

                            {sin.peritajeCampo && (
                              <div className="p-2.5 rounded-xl bg-white border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
                                <div className="flex items-center justify-between">
                                  <span>
                                    Perito: <strong className="text-slate-800">{sin.peritajeCampo.peritoNombre}</strong>
                                  </span>
                                  {sin.peritajeCampo.ocrPlacaDetectada && (
                                    <span className="font-mono text-emerald-700 font-semibold">
                                      Placa verificada: {sin.peritajeCampo.ocrPlacaDetectada}
                                    </span>
                                  )}
                                </div>
                                {sin.peritajeCampo.notas && (
                                  <p className="text-slate-500 italic">"{sin.peritajeCampo.notas}"</p>
                                )}
                              </div>
                            )}

                            <div className="pt-2.5 border-t border-slate-200/70 flex flex-wrap items-center justify-between gap-2 text-xs">
                              <div>
                                <span className="text-slate-500 block text-[11px]">
                                  Severidad: <strong className="text-indigo-700">{sin.triajeIa?.gravedad || 'MEDIA'}</strong>
                                </span>
                                <span className="font-mono font-bold text-slate-900">
                                  Indemnización: USD {(sin.montoIndemnizacionAprobado || sin.montoEstimadoReparacion || 0).toLocaleString()}
                                </span>
                              </div>

                              <a
                                href={evidenciaUrl}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 text-white text-[11px] font-semibold hover:bg-indigo-700 transition-colors"
                              >
                                <span className="material-symbols-outlined text-[14px]">photo_camera</span>
                                <span>Ver Evidencia (Amazon S3)</span>
                              </a>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>

                {/* Comprobantes Fiscales y Facturas Vinculadas con Acceso Directo a Pago QR */}
                <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className="material-symbols-outlined text-[#005C55]">receipt_long</span>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Facturas y Comprobantes de Póliza
                      </h2>
                    </div>
                    <span className="text-xs font-mono text-slate-500">
                      {resumenUnificado.pagosPendientes.length} Documento(s)
                    </span>
                  </div>

                  <div className="p-5 space-y-3">
                    {resumenUnificado.pagosPendientes.map((fac) => (
                      <div
                        key={fac.id}
                        className="p-3.5 rounded-xl border border-slate-200/90 bg-slate-50/50 flex flex-wrap items-center justify-between gap-3 text-xs"
                      >
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono font-bold text-slate-900">{fac.numeroFactura}</span>
                            <span
                              className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                                fac.estado === 'PAGADA'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {fac.estado}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 mt-0.5">
                            Total: <strong className="font-mono text-slate-800">USD {fac.total.toFixed(2)}</strong> ·{' '}
                            {fac.fechaEmision.slice(0, 10)}
                          </p>
                        </div>

                        <div className="flex items-center gap-2">
                          <a
                            href={fac.urlPdfAlmacenado || `${MS1_PUBLIC_URL}/api/v1/facturas/${fac.id}/pdf`}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-300 bg-white text-slate-700 font-semibold hover:bg-slate-50"
                          >
                            <span className="material-symbols-outlined text-[14px]">picture_as_pdf</span>
                            <span>PDF</span>
                          </a>
                          <button
                            type="button"
                            onClick={() => {
                              setQrForm((prev) => ({
                                ...prev,
                                polizaId: fac.polizaId || polizaPrincipal?.id || prev.polizaId,
                                facturaId: fac.id,
                                monto: fac.total
                              }));
                              setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
                              setActiveTab('facturacion_qr');
                              showToast('success', `Factura ${fac.numeroFactura} cargada en la pasarela QR.`);
                            }}
                            className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-[#005C55] text-white font-semibold hover:bg-[#0F766E]"
                          >
                            <span className="material-symbols-outlined text-[14px]">qr_code_2</span>
                            <span>Pagar QR</span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* =====================================================================
            SECCIÓN 2: COTIZAR Y EMITIR PÓLIZA CON VERIFICACIÓN DE DOCUMENTOS
        ===================================================================== */}
        {activeTab === 'cotizador' && (
          <div className="space-y-6">
            <div>
              <h1 className="font-heading text-2xl font-extrabold text-slate-900 tracking-tight">
                Cotizador Digital y Emisión Inmediata
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Personalice su cobertura vehicular, verifique la legibilidad de su documento y obtenga su póliza al instante.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Paso 1: Datos del Vehículo y Cálculo de Prima */}
              <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <span className="w-8 h-8 rounded-lg bg-teal-50 text-[#005C55] flex items-center justify-center font-bold text-xs">
                      1
                    </span>
                    <div>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Información del Vehículo y Plan
                      </h2>
                      <p className="text-xs text-slate-500">Complete las características para calcular su prima</p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="sm:col-span-2">
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Plan de Cobertura
                    </label>
                    <select
                      value={cotizadorForm.planId}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, planId: e.target.value })}
                      className="w-full px-3.5 py-2.5 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white transition-all"
                    >
                      {planes.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.nombre} — Base USD {p.primaBaseAnual}/año (Deducible {p.deducibleBasePorcentaje}%)
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Placa de Circulación
                    </label>
                    <input
                      type="text"
                      value={cotizadorForm.placa}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, placa: e.target.value })}
                      className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Valor Comercial (USD)
                    </label>
                    <input
                      type="number"
                      value={cotizadorForm.valorComercial}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, valorComercial: Number(e.target.value) })}
                      className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Marca
                    </label>
                    <input
                      type="text"
                      value={cotizadorForm.marca}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, marca: e.target.value })}
                      className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Modelo / Versión
                    </label>
                    <input
                      type="text"
                      value={cotizadorForm.modelo}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, modelo: e.target.value })}
                      className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Año de Fabricación
                    </label>
                    <input
                      type="number"
                      value={cotizadorForm.anio}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, anio: Number(e.target.value) })}
                      className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                      Ciudad de Circulación
                    </label>
                    <input
                      type="text"
                      value={cotizadorForm.ciudad}
                      onChange={(e) => setCotizadorForm({ ...cotizadorForm, ciudad: e.target.value })}
                      className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleCotizarPoliza}
                  disabled={loading || pendingAction !== null}
                  className="w-full py-3 px-4 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 active:scale-[0.99] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-2 shadow-sm"
                >
                  <span
                    className={`material-symbols-outlined text-[18px] ${
                      pendingAction === 'cotizar' ? 'animate-spin' : ''
                    }`}
                  >
                    {pendingAction === 'cotizar' ? 'progress_activity' : 'calculate'}
                  </span>
                  <span>
                    {pendingAction === 'cotizar' ? 'Calculando Cotización...' : 'Calcular Cotización'}
                  </span>
                </button>

                {cotizacionActual && (
                  <div className="p-4 rounded-2xl bg-gradient-to-br from-teal-50/90 to-emerald-50/50 border border-teal-200/80 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#005C55]">
                        Propuesta Económica Personalizada
                      </span>
                      <span className="font-mono text-[11px] px-2.5 py-0.5 rounded-full bg-white border border-teal-200 text-teal-900 font-semibold">
                        Deducible {cotizacionActual.deduciblePorcentaje}%
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2.5">
                      <div className="bg-white p-3 rounded-xl border border-teal-100">
                        <span className="text-[11px] text-slate-500 block">Prima Anual</span>
                        <span className="font-mono text-base font-bold text-slate-900">
                          USD {cotizacionActual.primaCalculadaAnual.toLocaleString()}
                        </span>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-teal-100">
                        <span className="text-[11px] text-slate-500 block">Cuota Mensual</span>
                        <span className="font-mono text-base font-bold text-[#005C55]">
                          USD {cotizacionActual.primaCalculadaMensual.toLocaleString()}
                        </span>
                      </div>
                      <div className="bg-white p-3 rounded-xl border border-teal-100">
                        <span className="text-[11px] text-slate-500 block">Bonificación</span>
                        <span className="font-mono text-base font-bold text-emerald-700">
                          -USD {cotizacionActual.descuentoScoreAplicado.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Paso 2: Verificación Inteligente de Documentos */}
              <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <span className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-xs">
                      2
                    </span>
                    <div>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Verificación Inteligente de Documento (RUAT / CI)
                      </h2>
                      <p className="text-xs text-slate-500">
                        Análisis automático de nitidez y legibilidad en su navegador
                      </p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200/80">
                    <span className="material-symbols-outlined text-[14px]">bolt</span>
                    IA en Navegador
                  </span>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => handleSimularDocumento('NITIDA_HD')}
                    className={`py-2 px-3 rounded-xl border text-xs font-semibold transition-all ${
                      modoEscaneoActual === 'NITIDA_HD' && validacionNitidez?.esValidoTfJs && !vistaMapaBordes
                        ? 'border-emerald-500 bg-emerald-50 text-emerald-900 shadow-xs'
                        : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    ✓ Probar Nítido (HD)
                  </button>
                  <button
                    type="button"
                    onClick={() => handleSimularDocumento('BORROSA_DESENFOCADA')}
                    className={`py-2 px-3 rounded-xl border text-xs font-semibold transition-all ${
                      modoEscaneoActual === 'BORROSA_DESENFOCADA' && !validacionNitidez?.esValidoTfJs
                        ? 'border-red-400 bg-red-50 text-red-900 shadow-xs'
                        : 'border-slate-200 bg-slate-50 text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    ✕ Probar Desenfocado
                  </button>
                  <button
                    type="button"
                    onClick={camaraActiva ? handleDetenerCamaraWeb : handleIniciarCamaraWeb}
                    className={`py-2 px-3 rounded-xl border text-xs font-semibold transition-all inline-flex items-center gap-1.5 ${
                      camaraActiva
                        ? 'border-red-400 bg-red-50 text-red-900'
                        : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <span className="material-symbols-outlined text-[16px]">
                      {camaraActiva ? 'videocam_off' : 'photo_camera'}
                    </span>
                    <span>{camaraActiva ? 'Cerrar Cámara' : 'Usar Cámara Web'}</span>
                  </button>
                  {camaraActiva && (
                    <button
                      type="button"
                      onClick={handleCapturarFotoCamara}
                      className="py-2 px-3 rounded-xl bg-teal-700 text-white text-xs font-bold transition-all inline-flex items-center gap-1.5 shadow-sm active:scale-95 animate-pulse"
                    >
                      <span className="material-symbols-outlined text-[16px]">camera</span>
                      <span>Capturar Foto del Documento</span>
                    </button>
                  )}
                  <label className="cursor-pointer inline-flex items-center gap-1.5 py-2 px-3 rounded-xl border border-slate-300 bg-white text-slate-700 text-xs font-semibold hover:bg-slate-50">
                    <span className="material-symbols-outlined text-[16px]">upload_file</span>
                    <span>Subir Foto</span>
                    <input type="file" accept="image/*" onChange={handleArchivoSubido} className="hidden" />
                  </label>
                  <button
                    type="button"
                    onClick={handleAlternarMapaBordesIA}
                    className={`py-2 px-3 rounded-xl border text-xs font-semibold transition-all inline-flex items-center gap-1.5 ${
                      vistaMapaBordes
                        ? 'border-emerald-500 bg-slate-900 text-emerald-400 font-mono shadow-xs'
                        : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <span className="material-symbols-outlined text-[16px]">insights</span>
                    <span>{vistaMapaBordes ? 'Ver Documento Original' : 'Ver Mapa de Bordes IA'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRespaldarDocumentoS3()}
                    disabled={pendingAction === 'subir-s3'}
                    className="py-2 px-3 rounded-xl border border-teal-200 bg-teal-50 text-[#005C55] text-xs font-semibold hover:bg-teal-100 transition-all inline-flex items-center gap-1.5"
                  >
                    <span className={`material-symbols-outlined text-[16px] ${pendingAction === 'subir-s3' ? 'animate-spin' : ''}`}>
                      {pendingAction === 'subir-s3' ? 'progress_activity' : 'cloud_upload'}
                    </span>
                    <span>{pendingAction === 'subir-s3' ? 'Respaldando...' : 'Respaldar en Amazon S3'}</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center">
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDraggingDoc(true);
                    }}
                    onDragLeave={() => setIsDraggingDoc(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDraggingDoc(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) procesarArchivoImagen(file);
                    }}
                    className={`sm:col-span-6 rounded-2xl border-2 border-dashed p-3 flex flex-col items-center justify-center transition-all ${
                      isDraggingDoc
                        ? 'border-emerald-500 bg-emerald-50/60 ring-2 ring-emerald-200'
                        : 'border-slate-300 bg-slate-100/80 hover:border-slate-400'
                    }`}
                  >
                    {camaraActiva ? (
                      <div className="w-full relative">
                        <video
                          ref={videoRef}
                          autoPlay
                          playsInline
                          muted
                          className="w-full h-auto rounded-lg shadow-xs border border-slate-300 bg-black aspect-video object-cover"
                        />
                        <div className="absolute inset-0 border-2 border-teal-400/80 rounded-lg pointer-events-none flex items-center justify-center">
                          <div className="border border-white/70 border-dashed rounded w-4/5 h-3/5 flex items-end justify-center pb-2">
                            <span className="text-[10px] font-mono text-white bg-black/70 px-2 py-0.5 rounded">
                              Encuadre Documento Aquí
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <canvas
                        ref={docCanvasRef}
                        width={300}
                        height={165}
                        className="w-full h-auto rounded-lg shadow-xs border border-slate-300 bg-white"
                      />
                    )}
                    <span className="text-[10px] text-slate-500 mt-2 text-center">
                      {camaraActiva
                        ? 'Transmisión de cámara web en vivo activa · Alinee su RUAT o Cédula'
                        : isDraggingDoc
                        ? 'Suelte el archivo aquí para analizar nitidez con IA'
                        : 'Arrastre y suelte una foto del RUAT/Cédula aquí, o use la cámara web'}
                    </span>
                  </div>

                  {validacionNitidez && (
                    <div
                      className={`sm:col-span-6 p-4 rounded-2xl border space-y-2.5 ${
                        validacionNitidez.esValidoTfJs
                          ? 'bg-emerald-50/70 border-emerald-200 text-emerald-950'
                          : 'bg-red-50/70 border-red-200 text-red-950'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold">
                          {validacionNitidez.esValidoTfJs ? 'Documento Aprobado' : 'Calidad Insuficiente'}
                        </span>
                        <span className="font-mono text-[11px] px-2 py-0.5 rounded-full bg-white/90 font-semibold">
                          {validacionNitidez.tiempoInferenciaMs} ms
                        </span>
                      </div>

                      <div>
                        <div className="flex items-baseline justify-between">
                          <span className="text-xs opacity-80">Índice de Nitidez</span>
                          <span className="font-mono text-xl font-bold">
                            {Math.round(validacionNitidez.nitidezScore * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-white/80 h-2 rounded-full mt-1 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-300 ${
                              validacionNitidez.esValidoTfJs ? 'bg-emerald-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${Math.round(validacionNitidez.nitidezScore * 100)}%` }}
                          />
                        </div>
                      </div>

                      <p className="text-[11px] leading-relaxed opacity-90">
                        {validacionNitidez.esValidoTfJs
                          ? 'Bordes y textos legibles verificados correctamente para la suscripción.'
                          : 'Se detectó desenfoque en la imagen. Por favor capture una fotografía más clara.'}
                      </p>
                    </div>
                  )}
                </div>

                {documentoS3Info && (
                  <div className="p-3.5 rounded-2xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 text-xs space-y-2 shadow-xs">
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center gap-1.5 font-bold text-emerald-950">
                        <span className="material-symbols-outlined text-[18px] text-[#005C55]">cloud_done</span>
                        <span>Documento Respaldado en Amazon S3</span>
                      </span>
                      <a
                        href={documentoS3Info.s3Url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[#005C55] text-white text-[11px] font-semibold hover:bg-[#0F766E] transition-colors"
                      >
                        <span>Abrir en AWS S3</span>
                        <span className="material-symbols-outlined text-[13px]">open_in_new</span>
                      </a>
                    </div>
                    <div className="font-mono text-[10px] text-slate-700 bg-white/90 p-2 rounded-xl border border-emerald-100 break-all">
                      <span className="font-bold text-slate-900 block mb-0.5">URL Pública S3:</span>
                      {documentoS3Info.s3Url}
                    </div>
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-600 px-1">
                      <span>Bucket: {documentoS3Info.bucket}</span>
                      <span className="truncate max-w-[240px]">SHA-256: {documentoS3Info.hashSha256}</span>
                    </div>
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleEmitirPoliza}
                  disabled={loading || pendingAction !== null || !validacionNitidez?.esValidoTfJs}
                  className={`w-full py-3.5 px-4 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2 shadow-sm active:scale-[0.99] ${
                    validacionNitidez?.esValidoTfJs
                      ? 'bg-[#005C55] text-white hover:bg-[#0F766E] disabled:opacity-60 disabled:cursor-wait'
                      : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                  }`}
                >
                  <span
                    className={`material-symbols-outlined text-[18px] ${
                      pendingAction === 'emitir-poliza' ? 'animate-spin' : ''
                    }`}
                  >
                    {pendingAction === 'emitir-poliza' ? 'progress_activity' : 'verified'}
                  </span>
                  <span>
                    {pendingAction === 'emitir-poliza'
                      ? 'Emitiendo Póliza Digital...'
                      : isOffline
                      ? 'Guardar Emisión en Cola Sin Conexión'
                      : 'Emitir Póliza Digital Ahora'}
                  </span>
                </button>

                {polizaRecienEmitida && (
                  <div className="p-4 rounded-2xl bg-slate-900 text-white text-xs space-y-1.5">
                    <div className="flex items-center justify-between text-emerald-400 font-bold">
                      <span>✓ Póliza Emitida: {polizaRecienEmitida.numeroPoliza}</span>
                      <span className="font-mono px-2 py-0.5 rounded bg-emerald-500/20">
                        {polizaRecienEmitida.estado}
                      </span>
                    </div>
                    <p className="text-slate-300">
                      Vigencia: <span className="font-mono">{polizaRecienEmitida.fechaInicio.slice(0, 10)}</span> al{' '}
                      <span className="font-mono">{polizaRecienEmitida.fechaFin.slice(0, 10)}</span> · Cobertura Activa:{' '}
                      <strong className="font-mono text-teal-300">
                        USD {polizaRecienEmitida.saldoCoberturaRestante.toLocaleString()}
                      </strong>
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* =====================================================================
            SECCIÓN 3: PLANES COMERCIALES, COBERTURAS Y DIRECTORIO DE ASEGURADOS
        ===================================================================== */}
        {activeTab === 'catalogo' && (
          <div className="space-y-6">
            <div>
              <h1 className="font-heading text-2xl font-extrabold text-slate-900 tracking-tight">
                Catálogo de Planes de Seguro, Coberturas y Clientes
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Configure nuevos planes de protección, agregue coberturas específicas, active o pause planes y gestione asegurados.
              </p>
            </div>

            {/* Barra de Filtros por Ramo y Búsqueda de Planes */}
            <div className="bg-white rounded-2xl border border-slate-200/90 p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-xs font-semibold text-slate-500 mr-1.5">Filtrar Ramo:</span>
                {(['TODOS', 'VEHICULAR', 'SALUD', 'VIDA', 'HOGAR'] as const).map((ramo) => {
                  const count = ramo === 'TODOS' ? planes.length : planes.filter((p) => p.tipo === ramo).length;
                  const isSelected = filtroRamoPlan === ramo;
                  return (
                    <button
                      key={ramo}
                      type="button"
                      onClick={() => setFiltroRamoPlan(ramo)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all inline-flex items-center gap-1.5 ${
                        isSelected
                          ? 'bg-[#005C55] text-white shadow-xs'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                      }`}
                    >
                      <span>{ramo}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded-full font-mono ${
                          isSelected ? 'bg-white/20 text-white' : 'bg-white text-slate-600'
                        }`}
                      >
                        {count}
                      </span>
                    </button>
                  );
                })}
              </div>

              <div className="relative w-full md:w-72">
                <span className="material-symbols-outlined text-[18px] text-slate-400 absolute left-3 top-2.5">
                  search
                </span>
                <input
                  type="text"
                  placeholder="Buscar plan por nombre o código..."
                  value={busquedaPlanes}
                  onChange={(e) => setBusquedaPlanes(e.target.value)}
                  className="w-full pl-9 pr-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                />
              </div>
            </div>

            {/* Tarjetas de Planes Activos y Pausados */}
            {(() => {
              const planesFiltrados = planes.filter((plan) => {
                const matchRamo = filtroRamoPlan === 'TODOS' || plan.tipo === filtroRamoPlan;
                const q = busquedaPlanes.trim().toLowerCase();
                const matchBusqueda =
                  !q ||
                  plan.nombre.toLowerCase().includes(q) ||
                  plan.codigo.toLowerCase().includes(q) ||
                  (plan.descripcion && plan.descripcion.toLowerCase().includes(q));
                return matchRamo && matchBusqueda;
              });

              if (planesFiltrados.length === 0) {
                return (
                  <div className="bg-white rounded-2xl border border-slate-200/90 p-8 text-center text-xs text-slate-500">
                    No se encontraron planes que coincidan con el filtro seleccionado.
                  </div>
                );
              }

              return (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                  {planesFiltrados.map((plan) => (
                    <div
                      key={plan.id}
                      className={`bg-white rounded-2xl border p-5 shadow-sm flex flex-col justify-between space-y-4 transition-all ${
                        plan.activo !== false ? 'border-slate-200/90' : 'border-amber-200/80 bg-amber-50/20'
                      }`}
                    >
                      <div>
                        <div className="flex items-center justify-between">
                          <span className="font-mono text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-teal-50 text-[#005C55] border border-teal-200">
                            {plan.codigo}
                          </span>
                          <div className="flex items-center gap-1.5">
                            <span
                              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                                plan.activo !== false
                                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                                  : 'bg-amber-50 text-amber-800 border-amber-200'
                              }`}
                            >
                              {plan.activo !== false ? '● Activo' : '○ Pausado'}
                            </span>
                            <span className="text-xs font-semibold text-slate-400">{plan.tipo}</span>
                          </div>
                        </div>

                        <h3 className="font-heading text-base font-bold text-slate-900 mt-2.5">
                          {plan.nombre}
                        </h3>
                        <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                          {plan.descripcion || 'Cobertura integral con asistencia inmediata.'}
                        </p>

                        <div className="mt-4 pt-3 border-t border-slate-100 space-y-1.5">
                          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">
                            Coberturas Incluidas ({plan.coberturas.length})
                          </span>
                          {plan.coberturas.map((c) => (
                            <div key={c.id} className="flex items-center justify-between text-xs py-0.5">
                              <span className="text-slate-700 truncate pr-2">• {c.nombre}</span>
                              <span className="font-mono font-semibold text-slate-900 shrink-0">
                                USD {c.sumaAseguradaMax.toLocaleString()}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-100 space-y-3">
                        <div className="flex items-baseline justify-between">
                          <div>
                            <span className="text-[11px] text-slate-400 block">Prima Base Anual</span>
                            <span className="font-mono text-lg font-bold text-[#005C55]">
                              USD {plan.primaBaseAnual}
                            </span>
                          </div>
                          <span className="text-xs font-semibold text-slate-600">
                            Deducible {plan.deducibleBasePorcentaje}%
                          </span>
                        </div>

                        {/* Botones de Acción Comercial */}
                        <div className="grid grid-cols-2 gap-2 pt-1">
                          <button
                            type="button"
                            onClick={() => handleToggleEstadoPlan(plan)}
                            disabled={pendingAction === `toggle-plan-${plan.id}`}
                            className={`py-2 px-2.5 rounded-xl text-xs font-semibold border transition-all flex items-center justify-center gap-1 active:scale-95 ${
                              plan.activo !== false
                                ? 'border-amber-300 bg-amber-50 text-amber-900 hover:bg-amber-100'
                                : 'border-emerald-300 bg-emerald-50 text-emerald-900 hover:bg-emerald-100'
                            }`}
                          >
                            <span className="material-symbols-outlined text-[15px]">
                              {plan.activo !== false ? 'pause_circle' : 'play_circle'}
                            </span>
                            <span>{plan.activo !== false ? 'Pausar Plan' : 'Activar Plan'}</span>
                          </button>

                          <button
                            type="button"
                            onClick={() => handleSeleccionarPlanParaCotizar(plan)}
                            className="py-2 px-2.5 rounded-xl bg-[#005C55] text-white text-xs font-semibold hover:bg-[#0F766E] transition-all flex items-center justify-center gap-1 shadow-xs active:scale-95"
                          >
                            <span className="material-symbols-outlined text-[15px]">calculate</span>
                            <span>Cotizar con este Plan</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}

            {/* Directorio de Asegurados Registrados */}
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden space-y-0">
              <div className="px-6 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <span className="w-8 h-8 rounded-xl bg-teal-50 text-[#005C55] flex items-center justify-center">
                    <span className="material-symbols-outlined text-[18px]">group</span>
                  </span>
                  <div>
                    <h3 className="font-heading text-base font-bold text-slate-900">
                      Directorio de Asegurados Registrados
                    </h3>
                    <p className="text-xs text-slate-500">Seleccione un asegurado para cotizar o consultar su expediente</p>
                  </div>
                </div>

                <div className="relative w-full md:w-72">
                  <span className="material-symbols-outlined text-[18px] text-slate-400 absolute left-3 top-2.5">
                    search
                  </span>
                  <input
                    type="text"
                    placeholder="Buscar por nombre, documento o ciudad..."
                    value={busquedaClientes}
                    onChange={(e) => setBusquedaClientes(e.target.value)}
                    className="w-full pl-9 pr-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55] focus:bg-white"
                  />
                </div>
              </div>

              {(() => {
                const clientesFiltrados = clientesList.filter((c) => {
                  const q = busquedaClientes.trim().toLowerCase();
                  if (!q) return true;
                  return (
                    c.nombreCompleto.toLowerCase().includes(q) ||
                    c.numeroDocumento.toLowerCase().includes(q) ||
                    (c.email && c.email.toLowerCase().includes(q)) ||
                    (c.ciudad && c.ciudad.toLowerCase().includes(q))
                  );
                });

                if (clientesFiltrados.length === 0) {
                  return (
                    <div className="p-8 text-center text-xs text-slate-500">
                      No se encontraron asegurados que coincidan con la búsqueda.
                    </div>
                  );
                }

                return (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="bg-slate-50 text-slate-500 border-b border-slate-200/80">
                          <th className="py-3 px-4 font-semibold">Asegurado</th>
                          <th className="py-3 px-4 font-semibold">Documento</th>
                          <th className="py-3 px-4 font-semibold">Contacto</th>
                          <th className="py-3 px-4 font-semibold">Ciudad</th>
                          <th className="py-3 px-4 font-semibold">Score / Riesgo</th>
                          <th className="py-3 px-4 font-semibold text-right">Acciones</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {clientesFiltrados.map((cli) => {
                          const esActivo = cli.id === clienteActivoId;
                          return (
                            <tr key={cli.id} className={`hover:bg-slate-50/70 ${esActivo ? 'bg-teal-50/40' : ''}`}>
                              <td className="py-3 px-4">
                                <div className="flex items-center gap-2.5">
                                  <div className="w-8 h-8 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs">
                                    {cli.nombres.charAt(0)}{cli.apellidos.charAt(0)}
                                  </div>
                                  <div>
                                    <span className="font-bold text-slate-900 block">{cli.nombreCompleto}</span>
                                    {esActivo && (
                                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-teal-800 bg-teal-100 px-1.5 py-0.2 rounded">
                                        ● Activo en Sesión
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </td>
                              <td className="py-3 px-4 font-mono font-semibold text-slate-800">
                                {cli.tipoDocumento} {cli.numeroDocumento}
                              </td>
                              <td className="py-3 px-4 text-slate-600">
                                <span className="block truncate max-w-[180px]">{cli.email}</span>
                                <span className="font-mono text-[11px] text-slate-500">{cli.telefono}</span>
                              </td>
                              <td className="py-3 px-4 text-slate-700">{cli.ciudad}</td>
                              <td className="py-3 px-4">
                                <span className="font-mono font-bold text-slate-900 mr-2">{cli.scoreCrediticio}</span>
                                <span
                                  className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                                    cli.perfilRiesgo === 'BAJO'
                                      ? 'bg-emerald-100 text-emerald-800'
                                      : cli.perfilRiesgo === 'MODERADO'
                                      ? 'bg-amber-100 text-amber-800'
                                      : 'bg-red-100 text-red-800'
                                  }`}
                                >
                                  {cli.perfilRiesgo}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-right">
                                <div className="inline-flex items-center gap-2">
                                  <button
                                    type="button"
                                    onClick={() => handleSelectClienteActivo(cli.id)}
                                    className={`px-3 py-1.5 rounded-xl font-semibold transition-all text-xs ${
                                      esActivo
                                        ? 'bg-teal-100 text-teal-900 cursor-default'
                                        : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                                    }`}
                                  >
                                    {esActivo ? 'Seleccionado' : 'Seleccionar'}
                                  </button>
                                  <button
                                    type="button"
                                    onClick={() => {
                                      handleSelectClienteActivo(cli.id);
                                      setActiveTab('cotizador');
                                      showToast('success', `Asegurado ${cli.nombreCompleto} listo para cotización.`);
                                    }}
                                    className="px-3 py-1.5 rounded-xl bg-[#005C55] text-white font-semibold hover:bg-[#0F766E] transition-all text-xs inline-flex items-center gap-1 shadow-xs"
                                  >
                                    <span className="material-symbols-outlined text-[14px]">request_quote</span>
                                    <span>Cotizar Póliza</span>
                                  </button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                );
              })()}
            </div>

            {/* 3 Formularios de Gestión Comercial */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <form
                onSubmit={handleCrearPlan}
                className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-3.5"
              >
                <div className="flex items-center gap-2.5 border-b border-slate-100 pb-3">
                  <span className="material-symbols-outlined text-[#005C55]">add_moderator</span>
                  <h2 className="font-heading text-sm font-bold text-slate-900">
                    Nuevo Plan de Cobertura
                  </h2>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Código</label>
                    <input
                      type="text"
                      value={nuevoPlanForm.codigo}
                      onChange={(e) => setNuevoPlanForm({ ...nuevoPlanForm, codigo: e.target.value })}
                      className="w-full px-3 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Prima Anual (USD)</label>
                    <input
                      type="number"
                      value={nuevoPlanForm.primaBaseAnual}
                      onChange={(e) => setNuevoPlanForm({ ...nuevoPlanForm, primaBaseAnual: Number(e.target.value) })}
                      className="w-full px-3 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Nombre Comercial</label>
                  <input
                    type="text"
                    value={nuevoPlanForm.nombre}
                    onChange={(e) => setNuevoPlanForm({ ...nuevoPlanForm, nombre: e.target.value })}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading || pendingAction !== null}
                  className="w-full py-2.5 rounded-xl bg-[#005C55] text-white text-xs font-semibold hover:bg-[#0F766E] active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-1.5"
                >
                  {pendingAction === 'crear-plan' && (
                    <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                  )}
                  <span>{pendingAction === 'crear-plan' ? 'Guardando Plan...' : 'Guardar Plan'}</span>
                </button>
              </form>

              <form
                onSubmit={handleAgregarCobertura}
                className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-3.5"
              >
                <div className="flex items-center gap-2.5 border-b border-slate-100 pb-3">
                  <span className="material-symbols-outlined text-indigo-600">library_add</span>
                  <h2 className="font-heading text-sm font-bold text-slate-900">
                    Añadir Cobertura a Plan
                  </h2>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Plan Destino</label>
                  <select
                    value={nuevaCoberturaForm.planId}
                    onChange={(e) => setNuevaCoberturaForm({ ...nuevaCoberturaForm, planId: e.target.value })}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                  >
                    {planes.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.codigo} — {p.nombre}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Nombre Cobertura</label>
                    <input
                      type="text"
                      value={nuevaCoberturaForm.nombre}
                      onChange={(e) => setNuevaCoberturaForm({ ...nuevaCoberturaForm, nombre: e.target.value })}
                      className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Suma Máx. (USD)</label>
                    <input
                      type="number"
                      value={nuevaCoberturaForm.sumaAseguradaMax}
                      onChange={(e) =>
                        setNuevaCoberturaForm({ ...nuevaCoberturaForm, sumaAseguradaMax: Number(e.target.value) })
                      }
                      className="w-full px-3 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading || pendingAction !== null}
                  className="w-full py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-700 active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-1.5"
                >
                  {pendingAction === 'agregar-cobertura' && (
                    <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                  )}
                  <span>
                    {pendingAction === 'agregar-cobertura'
                      ? 'Vinculando Cobertura...'
                      : 'Vincular Cobertura al Plan'}
                  </span>
                </button>
              </form>

              <form
                onSubmit={handleCrearCliente}
                className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-3.5"
              >
                <div className="flex items-center gap-2.5 border-b border-slate-100 pb-3">
                  <span className="material-symbols-outlined text-emerald-700">person_add</span>
                  <h2 className="font-heading text-sm font-bold text-slate-900">
                    Registrar Nuevo Asegurado
                  </h2>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Documento CI / NIT</label>
                    <input
                      type="text"
                      value={nuevoClienteForm.numeroDocumento}
                      onChange={(e) =>
                        setNuevoClienteForm({ ...nuevoClienteForm, numeroDocumento: e.target.value })
                      }
                      className="w-full px-3 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Ciudad</label>
                    <input
                      type="text"
                      value={nuevoClienteForm.ciudad}
                      onChange={(e) => setNuevoClienteForm({ ...nuevoClienteForm, ciudad: e.target.value })}
                      className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Nombres</label>
                    <input
                      type="text"
                      value={nuevoClienteForm.nombres}
                      onChange={(e) => setNuevoClienteForm({ ...nuevoClienteForm, nombres: e.target.value })}
                      className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">Apellidos</label>
                    <input
                      type="text"
                      value={nuevoClienteForm.apellidos}
                      onChange={(e) => setNuevoClienteForm({ ...nuevoClienteForm, apellidos: e.target.value })}
                      className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      required
                    />
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading || pendingAction !== null}
                  className="w-full py-2.5 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-1.5"
                >
                  {pendingAction === 'crear-cliente' && (
                    <span className="material-symbols-outlined text-[16px] animate-spin">progress_activity</span>
                  )}
                  <span>
                    {pendingAction === 'crear-cliente' ? 'Registrando Asegurado...' : 'Registrar Asegurado'}
                  </span>
                </button>
              </form>
            </div>
          </div>
        )}

        {/* =====================================================================
            SECCIÓN 4: CONTRATACIÓN EXPRESS WHATSAPP, FACTURA PDF Y PAGOS QR SANDBOX
        ===================================================================== */}
        {activeTab === 'facturacion_qr' && (
          <div className="space-y-6">
            <div>
              <h1 className="font-heading text-2xl font-extrabold text-slate-900 tracking-tight">
                Emisión Express por WhatsApp, Facturación Digital y Pasarela Bancaria QR
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Genere su póliza y factura fiscal en PDF de forma automática con n8n y Amazon S3, o liquide su prima en la pasarela bancaria Sandbox.
              </p>
            </div>

            {/* Indicador de Flujo Automatizado en 4 Pasos */}
            <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#005C55]">hub</span>
                  <h2 className="font-heading text-sm font-bold text-slate-900">
                    Flujo Automatizado de Contratación, Facturación y Almacenamiento
                  </h2>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-teal-50 text-[#005C55] border border-teal-200 font-semibold">
                  Orquestación n8n + DDD + S3
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-1">
                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold flex items-center justify-center">1</span>
                    <span className="material-symbols-outlined text-[16px] text-emerald-600">chat</span>
                  </div>
                  <span className="font-heading text-xs font-bold text-slate-900 block">1. Solicitud WhatsApp</span>
                  <p className="text-[11px] text-slate-500 leading-tight">Recepción de datos de vehículo y asegurado vía webhook</p>
                </div>

                <div className={`p-3.5 rounded-xl border space-y-1 transition-all ${
                  pendingAction === 'whatsapp-n8n'
                    ? 'bg-indigo-50 border-indigo-300 ring-2 ring-indigo-200 animate-pulse'
                    : 'bg-slate-50 border-slate-200/80'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-800 text-[11px] font-bold flex items-center justify-center">2</span>
                    <span className={`material-symbols-outlined text-[16px] ${pendingAction === 'whatsapp-n8n' ? 'animate-spin text-indigo-600' : 'text-slate-500'}`}>
                      sync_alt
                    </span>
                  </div>
                  <span className="font-heading text-xs font-bold text-slate-900 block">2. Orquestador n8n (:5678)</span>
                  <p className="text-[11px] text-slate-500 leading-tight">Validación de suscripción y reglas de negocio automatizadas</p>
                </div>

                <div className={`p-3.5 rounded-xl border space-y-1 transition-all ${
                  pedidoWhatsAppResult ? 'bg-teal-50 border-teal-300' : 'bg-slate-50 border-slate-200/80'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 text-[11px] font-bold flex items-center justify-center">3</span>
                    <span className="material-symbols-outlined text-[16px] text-[#005C55]">receipt_long</span>
                  </div>
                  <span className="font-heading text-xs font-bold text-slate-900 block">3. Suscripción y Factura PDF (:8001)</span>
                  <p className="text-[11px] text-slate-500 leading-tight">Emisión en motor transaccional con firma SHA-256</p>
                </div>

                <div className={`p-3.5 rounded-xl border space-y-1 transition-all ${
                  pedidoWhatsAppResult ? 'bg-emerald-50 border-emerald-300' : 'bg-slate-50 border-slate-200/80'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold flex items-center justify-center">4</span>
                    <span className="material-symbols-outlined text-[16px] text-emerald-700">cloud_upload</span>
                  </div>
                  <span className="font-heading text-xs font-bold text-slate-900 block">4. Almacenamiento Amazon S3</span>
                  <p className="text-[11px] text-slate-500 leading-tight">Publicación inmutable del comprobante fiscal PDF</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Emisión Express WhatsApp y Factura PDF */}
              <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <span className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
                      <span className="material-symbols-outlined text-[20px]">chat</span>
                    </span>
                    <div>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Contratación Rápida vía WhatsApp
                      </h2>
                      <p className="text-xs text-slate-500">Emisión instantánea de póliza y comprobante fiscal</p>
                    </div>
                  </div>
                </div>

                <form onSubmit={handleContratacionWhatsApp} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3.5">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Número de WhatsApp
                      </label>
                      <input
                        type="text"
                        value={whatsappForm.telefono}
                        onChange={(e) => setWhatsappForm({ ...whatsappForm, telefono: e.target.value })}
                        className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Placa del Vehículo
                      </label>
                      <input
                        type="text"
                        value={whatsappForm.placa}
                        onChange={(e) => setWhatsappForm({ ...whatsappForm, placa: e.target.value })}
                        className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Marca
                      </label>
                      <input
                        type="text"
                        value={whatsappForm.marca}
                        onChange={(e) => setWhatsappForm({ ...whatsappForm, marca: e.target.value })}
                        className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Modelo
                      </label>
                      <input
                        type="text"
                        value={whatsappForm.modelo}
                        onChange={(e) => setWhatsappForm({ ...whatsappForm, modelo: e.target.value })}
                        className="w-full px-3.5 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Plan Solicitado
                      </label>
                      <select
                        value={whatsappForm.plan_codigo}
                        onChange={(e) => setWhatsappForm({ ...whatsappForm, plan_codigo: e.target.value })}
                        className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl"
                      >
                        {planes.map((p) => (
                          <option key={p.id} value={p.codigo}>
                            {p.nombre}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1">
                        Valor Comercial (USD)
                      </label>
                      <input
                        type="number"
                        value={whatsappForm.valor_comercial}
                        onChange={(e) =>
                          setWhatsappForm({ ...whatsappForm, valor_comercial: Number(e.target.value) })
                        }
                        className="w-full px-3.5 py-2 text-xs font-mono bg-slate-50 border border-slate-300 rounded-xl"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || pendingAction !== null}
                    className="w-full py-3 px-4 rounded-xl bg-emerald-700 text-white text-xs font-semibold hover:bg-emerald-800 active:scale-[0.99] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-2 shadow-sm"
                  >
                    <span
                      className={`material-symbols-outlined text-[18px] ${
                        pendingAction === 'whatsapp-n8n' ? 'animate-spin' : ''
                      }`}
                    >
                      {pendingAction === 'whatsapp-n8n' ? 'progress_activity' : 'picture_as_pdf'}
                    </span>
                    <span>
                      {pendingAction === 'whatsapp-n8n'
                        ? 'Ejecutando Flujo n8n y Generando PDF...'
                        : 'Emitir Póliza y Generar Factura PDF'}
                    </span>
                  </button>
                </form>

                {/* Vista de Conversación de WhatsApp Business Interactiva */}
                <div className="rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden bg-slate-100">
                  {/* Encabezado WhatsApp */}
                  <div className="bg-[#075E54] text-white px-4 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center font-bold text-sm">
                          <span className="material-symbols-outlined text-[20px]">shield</span>
                        </div>
                        <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-400 border border-white rounded-full"></span>
                      </div>
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-bold text-xs tracking-wide">AegisCore Seguros</span>
                          <span className="material-symbols-outlined text-[14px] text-teal-200" title="Cuenta Comercial Oficial Verificada">
                            verified
                          </span>
                        </div>
                        <span className="text-[10px] text-teal-100 block">Cuenta de Empresa Oficial · Bot n8n</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 text-white/80">
                      <span className="material-symbols-outlined text-[18px]">videocam</span>
                      <span className="material-symbols-outlined text-[18px]">call</span>
                      <span className="material-symbols-outlined text-[18px]">more_vert</span>
                    </div>
                  </div>

                  {/* Cuerpo del Chat */}
                  <div className="p-4 space-y-3.5 bg-[#EFEAE2] min-h-[200px]">
                    <div className="text-center">
                      <span className="text-[10px] bg-white/80 text-slate-600 px-2.5 py-0.5 rounded-full shadow-2xs font-medium">
                        HOY · CONVERSACIÓN CIFRADA DE EXTREMO A EXTREMO
                      </span>
                    </div>

                    {/* Mensaje del Cliente (Entrada) */}
                    <div className="flex justify-end">
                      <div className="bg-[#D9FDD3] text-slate-900 rounded-2xl rounded-tr-xs p-3 max-w-[85%] text-xs shadow-2xs space-y-1">
                        <p className="leading-relaxed">
                          Hola, deseo contratar la póliza para mi vehículo{' '}
                          <strong>{whatsappForm.marca} {whatsappForm.modelo}</strong> ({whatsappForm.placa}), valor comercial{' '}
                          <strong>USD {whatsappForm.valor_comercial}</strong>. Plan:{' '}
                          <code className="font-mono bg-emerald-100 px-1 py-0.5 rounded text-[11px]">{whatsappForm.plan_codigo}</code>.{' '}
                          C.I.: <strong>{whatsappForm.numero_documento}</strong>.
                        </p>
                        <div className="flex items-center justify-end gap-1 text-[10px] text-slate-500 pt-0.5">
                          <span>14:32</span>
                          <span className="material-symbols-outlined text-[13px] text-sky-600">done_all</span>
                        </div>
                      </div>
                    </div>

                    {/* Mensaje de Respuesta del Bot */}
                    <div className="flex justify-start">
                      <div className="bg-white text-slate-900 rounded-2xl rounded-tl-xs p-3.5 max-w-[88%] text-xs shadow-2xs space-y-2.5">
                        {!pedidoWhatsAppResult ? (
                          <>
                            <div className="flex items-center gap-1.5 text-[#005C55] font-bold text-[11px]">
                              <span className="material-symbols-outlined text-[14px]">smart_toy</span>
                              <span>Asistente Virtual AegisCore</span>
                            </div>
                            <p className="leading-relaxed text-slate-700">
                              👋 ¡Hola! Hemos recibido los datos de su vehículo. Pulse el botón <strong>"Emitir Póliza y Generar Factura PDF"</strong> en el formulario superior para que nuestro flujo en n8n suscriba su póliza, cree la factura fiscal y publique su comprobante en Amazon S3.
                            </p>
                            <div className="text-[10px] text-slate-400 text-right">14:32</div>
                          </>
                        ) : (
                          <>
                            <div className="flex items-center justify-between text-emerald-800 font-bold text-[11px]">
                              <span className="inline-flex items-center gap-1">
                                <span className="material-symbols-outlined text-[14px] text-emerald-600">check_circle</span>
                                <span>Póliza y Factura Suscritas con Éxito</span>
                              </span>
                              <span className="font-mono text-[10px] bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                                Emitida
                              </span>
                            </div>
                            <p className="leading-relaxed text-slate-800">
                              {pedidoWhatsAppResult.mensaje_whatsapp}
                            </p>
                            <div className="bg-slate-50 p-2.5 rounded-xl border border-slate-200 font-mono text-[11px] space-y-1">
                              <div className="flex justify-between">
                                <span className="text-slate-500 font-sans">N° Póliza:</span>
                                <span className="font-bold text-slate-900">{pedidoWhatsAppResult.poliza.numeroPoliza}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-500 font-sans">N° Factura:</span>
                                <span className="font-bold text-[#005C55]">{pedidoWhatsAppResult.factura.numeroFactura}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-slate-500 font-sans">Total:</span>
                                <span className="font-bold text-slate-900">USD {pedidoWhatsAppResult.factura.total}</span>
                              </div>
                              <div className="pt-1 text-[10px] text-slate-500 truncate">
                                Hash SHA-256: {pedidoWhatsAppResult.hash_digital_sha256}
                              </div>
                            </div>

                            {/* Botones de Acción dentro del Chat */}
                            <div className="pt-1 flex flex-col sm:flex-row gap-2">
                              <a
                                href={pedidoWhatsAppResult.url_pdf}
                                target="_blank"
                                rel="noreferrer"
                                className="flex-1 py-2 px-3 rounded-xl bg-slate-900 text-white font-semibold text-center text-xs hover:bg-slate-800 transition-colors inline-flex items-center justify-center gap-1.5"
                              >
                                <span className="material-symbols-outlined text-[15px]">picture_as_pdf</span>
                                <span>Ver Factura PDF en S3</span>
                              </a>
                              <button
                                type="button"
                                onClick={handlePagarFacturaWhatsAppConQR}
                                className="flex-1 py-2 px-3 rounded-xl bg-[#005C55] text-white font-semibold text-center text-xs hover:bg-[#0F766E] transition-colors inline-flex items-center justify-center gap-1.5 shadow-xs active:scale-95"
                              >
                                <span className="material-symbols-outlined text-[15px]">qr_code_scanner</span>
                                <span>Pagar esta Factura con QR Ahora</span>
                              </button>
                            </div>
                            <div className="text-[10px] text-slate-400 text-right">14:33</div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {pedidoWhatsAppResult && (
                  <div className="p-5 rounded-2xl bg-emerald-50/80 border border-emerald-200 space-y-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-emerald-950 text-sm">
                        Factura Emitida: {pedidoWhatsAppResult.factura.numeroFactura}
                      </span>
                      <span className="font-mono px-2.5 py-1 rounded-full bg-white text-emerald-800 font-bold border border-emerald-200">
                        Total: USD {pedidoWhatsAppResult.factura.total}
                      </span>
                    </div>
                    <p className="text-slate-700 bg-white p-3 rounded-xl border border-emerald-100">
                      {pedidoWhatsAppResult.mensaje_whatsapp}
                    </p>
                    <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                      <span className="text-[11px] font-mono text-emerald-800">
                        Sello Digital: {pedidoWhatsAppResult.hash_digital_sha256.slice(0, 20)}...
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={handlePagarFacturaWhatsAppConQR}
                          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#005C55] text-white font-semibold hover:bg-[#0F766E] transition-colors shadow-xs active:scale-95"
                        >
                          <span className="material-symbols-outlined text-[16px]">qr_code_2</span>
                          <span>Pagar esta Factura con QR Ahora</span>
                        </button>
                        <a
                          href={pedidoWhatsAppResult.url_pdf}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white font-semibold hover:bg-slate-800 transition-colors"
                        >
                          <span className="material-symbols-outlined text-[16px]">download</span>
                          <span>Descargar Factura PDF</span>
                        </a>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Pasarela Bancaria Sandbox QR 100% Funcional */}
              <div
                ref={pasarelaQrSectionRef}
                className="lg:col-span-6 bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-4"
              >
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-2.5">
                    <span className="w-9 h-9 rounded-xl bg-teal-50 text-[#005C55] flex items-center justify-center">
                      <span className="material-symbols-outlined text-[20px]">qr_code_scanner</span>
                    </span>
                    <div>
                      <h2 className="font-heading text-base font-bold text-slate-900">
                        Pasarela Bancaria QR (Sandbox SIP / QR Simple)
                      </h2>
                      <p className="text-xs text-slate-500">
                        Liquidación inmediata en base de datos con protección frente a doble cobro
                      </p>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold bg-teal-50 text-[#005C55] border border-teal-200">
                    SIP Sandbox
                  </span>
                </div>

                {/* Controles configurables de la orden QR */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Póliza a Pagar</label>
                    <select
                      value={qrForm.polizaId}
                      onChange={(e) => {
                        const pid = e.target.value;
                        const pol = resumenUnificado?.polizasActivas.find((p) => p.id === pid);
                        setQrForm((prev) => ({
                          ...prev,
                          polizaId: pid,
                          monto: pol?.primaMensual || prev.monto
                        }));
                        setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
                      }}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl font-mono"
                    >
                      {(resumenUnificado?.polizasActivas || []).map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.numeroPoliza} ({p.bienAsegurado.placa})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Entidad Financiera Sandbox</label>
                    <select
                      value={qrForm.bancoSandbox}
                      onChange={(e) => setQrForm({ ...qrForm, bancoSandbox: e.target.value })}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl"
                    >
                      <option value="Banco Nacional de Bolivia (BNB · SIP QR Sandbox)">
                        Banco Nacional de Bolivia (BNB Sandbox)
                      </option>
                      <option value="Banco Mercantil Santa Cruz (BMSC · SIP Sandbox)">
                        Banco Mercantil Santa Cruz (BMSC Sandbox)
                      </option>
                      <option value="Banco Bisa (e-Bisa QR Simple Sandbox)">
                        Banco Bisa (QR Simple Sandbox)
                      </option>
                      <option value="Billetera Móvil Tigo Money (Sandbox)">
                        Billetera Móvil Tigo Money (Sandbox)
                      </option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Número de Cuota</label>
                    <input
                      type="number"
                      min={1}
                      max={12}
                      value={qrForm.numeroCuota}
                      onChange={(e) => {
                        setQrForm({ ...qrForm, numeroCuota: Number(e.target.value) });
                        setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
                      }}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl font-mono"
                    />
                  </div>

                  <div>
                    <label className="block font-semibold text-slate-700 mb-1">Importe a Debitar (USD)</label>
                    <input
                      type="number"
                      step="0.01"
                      min={1}
                      value={qrForm.monto}
                      onChange={(e) => {
                        setQrForm({ ...qrForm, monto: Number(e.target.value) });
                        setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
                      }}
                      className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-xl font-mono font-bold text-[#005C55]"
                    />
                  </div>
                </div>

                {/* Código QR Dinámico + Resumen de Orden */}
                <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center bg-slate-50/80 p-4 rounded-2xl border border-slate-200/80">
                  <div className="sm:col-span-4 flex flex-col items-center justify-center bg-white p-3 rounded-xl border border-slate-200">
                    <svg viewBox="0 0 100 100" className="w-28 h-28 text-slate-900" fill="currentColor">
                      <rect x="10" y="10" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="5" />
                      <rect x="16" y="16" width="12" height="12" />
                      <rect x="66" y="10" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="5" />
                      <rect x="72" y="16" width="12" height="12" />
                      <rect x="10" y="66" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="5" />
                      <rect x="16" y="72" width="12" height="12" />
                      <rect x="42" y="42" width="16" height="16" rx="3" fill="#005C55" />
                      {qrCells.map((c, idx) => (
                        <rect key={idx} x={c.x} y={c.y} width="5.5" height="5.5" rx="1" />
                      ))}
                    </svg>
                    <span className="font-mono text-[10px] text-slate-500 mt-1">
                      USD {qrForm.monto.toFixed(2)} · Cuota #{qrForm.numeroCuota}
                    </span>
                  </div>

                  <div className="sm:col-span-8 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Banco Procesador:</span>
                      <span className="font-semibold text-slate-900 truncate max-w-[200px]">
                        {qrForm.bancoSandbox}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-500">Total a Acreditar:</span>
                      <span className="font-mono text-base font-bold text-[#005C55]">
                        USD {qrForm.monto.toFixed(2)}
                      </span>
                    </div>
                    <div className="pt-2 border-t border-slate-200/80">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[11px] text-slate-500">Llave de Operación (Idempotency-Key):</span>
                        <button
                          type="button"
                          onClick={() => {
                            setQrKeyUuid(ApolloFederationClient.generarUUIDv4());
                            showToast('success', 'Nueva orden QR y llave UUID generadas.');
                          }}
                          className="text-[11px] text-[#005C55] font-semibold hover:underline active:scale-95 transition-transform"
                        >
                          Nueva Orden QR
                        </button>
                      </div>
                      <div className="font-mono text-[11px] bg-white px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-700 truncate">
                        {qrKeyUuid}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => handleEjecutarPagoQR(false)}
                    disabled={loading || pendingAction !== null}
                    className="py-3 px-4 rounded-xl bg-[#005C55] text-white text-xs font-semibold hover:bg-[#0F766E] active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all shadow-sm flex items-center justify-center gap-2"
                  >
                    {pendingAction === 'qr-pay' && (
                      <span className="material-symbols-outlined text-[16px] animate-spin">
                        progress_activity
                      </span>
                    )}
                    <span>
                      {pendingAction === 'qr-pay'
                        ? 'Procesando en Sandbox...'
                        : 'Autorizar Pago en Sandbox Ahora'}
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleEjecutarPagoQR(true)}
                    disabled={loading || pendingAction !== null}
                    className="py-3 px-4 rounded-xl border border-amber-300 bg-amber-50 text-amber-900 text-xs font-semibold hover:bg-amber-100 active:scale-[0.98] disabled:opacity-60 disabled:cursor-wait transition-all flex items-center justify-center gap-2"
                  >
                    {pendingAction === 'qr-retry' && (
                      <span className="material-symbols-outlined text-[16px] animate-spin">
                        progress_activity
                      </span>
                    )}
                    <span>
                      {pendingAction === 'qr-retry'
                        ? 'Verificando Idempotencia...'
                        : 'Reintentar Misma Orden (Probar Anti-Doble Cobro)'}
                    </span>
                  </button>
                </div>

                {qrPagoResult && (
                  <div
                    className={`p-4 rounded-2xl border text-xs space-y-2 ${
                      qrPagoResult.fueIdempotente
                        ? 'bg-amber-50 border-amber-200 text-amber-950'
                        : 'bg-teal-50/80 border-teal-200 text-teal-950'
                    }`}
                  >
                    <div className="flex items-center justify-between font-bold">
                      <span>
                        {qrPagoResult.fueIdempotente
                          ? '✓ Protección Activa: Cobro Duplicado Evitado'
                          : '✓ Transacción Bancaria Aprobada y Registrada'}
                      </span>
                      <span className="font-mono px-2 py-0.5 rounded bg-white/80">
                        {qrPagoResult.codigoAutorizacion}
                      </span>
                    </div>
                    <p className="opacity-85">
                      {qrPagoResult.fueIdempotente
                        ? 'El sistema detectó que esta orden ya fue cobrada y devolvió su comprobante original sin volver a debitar.'
                        : `Cargo de USD ${qrPagoResult.monto.toFixed(2)} procesado mediante ${qrPagoResult.bancoSandbox || qrForm.bancoSandbox}.`}
                    </p>
                    <div className="pt-1 flex items-center justify-between">
                      <span className="font-mono text-[10px] opacity-75">
                        {qrPagoResult.fechaPago.slice(0, 19).replace('T', ' ')} UTC
                      </span>
                      <a
                        href={qrPagoResult.sandboxVoucherUrl || `${MS1_PUBLIC_URL}/sandbox/qr-checkout/${qrPagoResult.id}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-900 text-white font-semibold hover:bg-slate-800"
                      >
                        <span className="material-symbols-outlined text-[14px]">receipt</span>
                        <span>Abrir Comprobante Bancario Sandbox</span>
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Historial Real de Pagos QR Registrados en Base de Datos */}
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#005C55]">history</span>
                  <h3 className="font-heading text-base font-bold text-slate-900">
                    Historial de Pagos QR Liquidados en Base de Datos
                  </h3>
                </div>
                <span className="text-xs font-mono text-slate-500">
                  {historialPagosQr.length} Transacción(es)
                </span>
              </div>

              {historialPagosQr.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-500">
                  Aún no hay pagos QR registrados en esta sesión. Pulse <strong>"Autorizar Pago en Sandbox Ahora"</strong> para procesar su primera cuota.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 text-slate-500 border-b border-slate-200/80">
                        <th className="py-3 px-4 font-semibold">Autorización</th>
                        <th className="py-3 px-4 font-semibold">Entidad Financiera Sandbox</th>
                        <th className="py-3 px-4 font-semibold">Cuota</th>
                        <th className="py-3 px-4 font-semibold">Monto</th>
                        <th className="py-3 px-4 font-semibold">Fecha UTC</th>
                        <th className="py-3 px-4 font-semibold text-right">Comprobante</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {historialPagosQr.map((item) => (
                        <tr key={item.id} className="hover:bg-slate-50/70">
                          <td className="py-3 px-4 font-mono font-bold text-slate-900">
                            {item.codigoAutorizacion}
                          </td>
                          <td className="py-3 px-4 text-slate-700">
                            {item.bancoSandbox || 'SIP / QR Simple Sandbox'}
                          </td>
                          <td className="py-3 px-4 font-mono">Cuota #{item.numeroCuota}</td>
                          <td className="py-3 px-4 font-mono font-bold text-[#005C55]">
                            USD {Number(item.monto).toFixed(2)}
                          </td>
                          <td className="py-3 px-4 font-mono text-slate-500">
                            {item.fechaPago.slice(0, 19).replace('T', ' ')}
                          </td>
                          <td className="py-3 px-4 text-right">
                            <a
                              href={`${MS1_PUBLIC_URL}/sandbox/qr-checkout/${item.id}`}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 text-[#005C55] font-semibold hover:underline"
                            >
                              <span>Ver Voucher</span>
                              <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* =====================================================================
            SECCIÓN 5: CUENTA Y SEGURIDAD (SINGLE SIGN-ON + SESIONES EN NUBE)
        ===================================================================== */}
        {activeTab === 'seguridad' && (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <h1 className="font-heading text-2xl font-extrabold text-slate-900 tracking-tight">
                  Cuenta y Acceso Corporativo Unificado
                </h1>
                <p className="text-sm text-slate-500 mt-0.5">
                  Gestione su identidad digital, verifique su credencial criptográfica y controle sus sesiones activas en todos los módulos.
                </p>
              </div>
              <button
                type="button"
                disabled={pendingAction !== null}
                onClick={() => handleCerrarSesionSSO('ALL')}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-rose-600 text-white text-xs font-semibold hover:bg-rose-700 active:scale-[0.98] disabled:opacity-60 transition-all shadow-sm"
              >
                <span className="material-symbols-outlined text-[18px]">logout</span>
                <span>
                  {pendingAction === 'logout-ALL'
                    ? 'Revocando Sesiones...'
                    : 'Cerrar Sesión Global en Todos los Dispositivos'}
                </span>
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* Columna Izquierda: Cambio Rápido de Perfil + Login Corporativo Personalizado */}
              <div className="lg:col-span-6 space-y-6">
                <div className="bg-white rounded-2xl border border-slate-200/90 p-6 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <h2 className="font-heading text-base font-bold text-slate-900">
                      Perfiles Corporativos Disponibles
                    </h2>
                    <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-teal-50 text-[#005C55]">
                      Cambio Instantáneo
                    </span>
                  </div>

                  <div className="space-y-2.5">
                    {PERFILES_SSO_DEMO.map((item) => {
                      const isSelected = sesionSSO.email === item.email;
                      const isSwitchingThis = pendingAction === `sso-${item.email}`;
                      return (
                        <button
                          key={item.email}
                          type="button"
                          disabled={pendingAction !== null}
                          onClick={() => handleSwitchSSOUser(item.email, item.rol)}
                          className={`w-full text-left p-4 rounded-2xl border transition-all active:scale-[0.99] disabled:opacity-60 disabled:cursor-wait ${
                            isSelected
                              ? 'border-[#005C55] bg-teal-50/50 shadow-xs'
                              : 'border-slate-200 hover:bg-slate-50'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="font-heading text-sm font-bold text-slate-900 flex items-center gap-2">
                              {isSwitchingThis && (
                                <span className="material-symbols-outlined text-[16px] text-[#005C55] animate-spin">
                                  progress_activity
                                </span>
                              )}
                              <span>{item.nombre}</span>
                            </span>
                            <span
                              className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${
                                isSelected ? 'bg-[#005C55] text-white' : 'bg-slate-100 text-slate-700'
                              }`}
                            >
                              {isSwitchingThis ? 'Cambiando...' : item.rol}
                            </span>
                          </div>
                          <p className="text-xs text-slate-500 mt-1">{item.email}</p>
                        </button>
                      );
                    })}
                  </div>

                  {/* Formulario de Inicio de Sesión con Correo Corporativo Personalizado */}
                  <form
                    onSubmit={handleCustomLoginSSO}
                    className="pt-4 border-t border-slate-100 space-y-3"
                  >
                    <p className="text-xs font-bold text-slate-800">
                      Iniciar sesión con otra cuenta corporativa
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
                      <input
                        type="email"
                        required
                        value={customLoginForm.email}
                        onChange={(e) => setCustomLoginForm({ ...customLoginForm, email: e.target.value })}
                        placeholder="correo@empresa.com"
                        className="sm:col-span-2 px-3 py-2 text-xs bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55]"
                      />
                      <select
                        value={customLoginForm.rol}
                        onChange={(e) => setCustomLoginForm({ ...customLoginForm, rol: e.target.value })}
                        className="px-3 py-2 text-xs font-semibold bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:border-[#005C55]"
                      >
                        <option value="CLIENTE">CLIENTE</option>
                        <option value="ADMIN">ADMIN</option>
                        <option value="PERITO">PERITO</option>
                        <option value="ACTUARIO">ACTUARIO</option>
                        <option value="AJUSTADOR">AJUSTADOR</option>
                      </select>
                    </div>
                    <button
                      type="submit"
                      disabled={pendingAction !== null}
                      className="w-full py-2.5 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 disabled:opacity-60 transition-colors"
                    >
                      Autenticar y Emitir Token OIDC PKCE
                    </button>
                  </form>
                </div>
              </div>

              {/* Columna Derecha: Estado de Sesión Segura + Inspector de Token JWT RS256 */}
              <div className="lg:col-span-6 bg-slate-900 text-slate-100 rounded-2xl p-6 shadow-sm flex flex-col justify-between space-y-5">
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                    <div className="flex items-center gap-2.5">
                      <span className="material-symbols-outlined text-teal-400">verified_user</span>
                      <span className="font-heading text-base font-bold text-white">
                        Estado de Sesión Segura (OAuth 2.0 + OIDC PKCE)
                      </span>
                    </div>
                    <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-semibold">
                      Activa · RS256
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80">
                      <span className="text-slate-400 block">Identificador de Sesión</span>
                      <span className="font-mono text-white font-semibold mt-0.5 block truncate">
                        {sesionSSO.session_id}
                      </span>
                    </div>
                    <div className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/80">
                      <span className="text-slate-400 block">Nivel de Acceso y Protocolo</span>
                      <span className="font-mono text-teal-300 font-semibold mt-0.5 block">
                        {sesionSSO.rol} · PKCE S256
                      </span>
                    </div>
                  </div>

                  {/* Inspector de Credencial Digital JWT RS256 Decodificado */}
                  <div className="rounded-xl bg-slate-950/90 border border-slate-800 p-4 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <button
                        type="button"
                        onClick={() => setMostrarInspectorJwt(!mostrarInspectorJwt)}
                        className="text-xs font-semibold text-teal-300 flex items-center gap-1 hover:underline"
                      >
                        <span className="material-symbols-outlined text-[15px]">code</span>
                        <span>
                          {mostrarInspectorJwt
                            ? 'Ocultar Credencial JWT RS256 Decodificada'
                            : 'Ver Credencial JWT RS256 Decodificada'}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          if (navigator.clipboard) {
                            navigator.clipboard.writeText(sesionSSO.access_token);
                            showToast('success', 'Token JWT RS256 copiado al portapapeles.');
                          }
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800 text-slate-200 text-[11px] font-semibold hover:bg-slate-700"
                      >
                        <span className="material-symbols-outlined text-[13px]">content_copy</span>
                        <span>Copiar JWT</span>
                      </button>
                    </div>

                    {mostrarInspectorJwt && (
                      <pre className="text-[11px] font-mono text-emerald-300/95 overflow-x-auto max-h-48 leading-relaxed">
                        {JSON.stringify(jwtDecodificado, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-800 flex flex-wrap gap-3">
                  <a
                    href="http://localhost:8080"
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-[#005C55] text-white text-xs font-semibold hover:bg-[#0F766E] transition-colors"
                  >
                    <span>Portal de Acceso Unificado (:8080)</span>
                    <span className="material-symbols-outlined text-[16px]">open_in_new</span>
                  </a>
                  <a
                    href="http://localhost:4200"
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 text-slate-200 text-xs font-semibold hover:bg-slate-700 transition-colors"
                  >
                    <span>Centro Actuarial &amp; BI (:4200)</span>
                    <span className="material-symbols-outlined text-[16px]">monitoring</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Tabla de Sesiones SSO Registradas en Amazon DynamoDB */}
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#005C55]">dns</span>
                  <h3 className="font-heading text-base font-bold text-slate-900">
                    Registro de Sesiones Corporativas en Nube (Amazon DynamoDB)
                  </h3>
                </div>
                <span className="text-xs font-mono text-slate-500">
                  {sesionesSSOList.length} Sesión(es) registrada(s)
                </span>
              </div>

              {sesionesSSOList.length === 0 ? (
                <div className="p-6 text-center text-xs text-slate-500">
                  Seleccione un perfil arriba para registrar y visualizar su sesión unificada en Amazon DynamoDB.
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="bg-slate-50 text-slate-500 border-b border-slate-200/80">
                        <th className="py-3 px-4 font-semibold">ID de Sesión</th>
                        <th className="py-3 px-4 font-semibold">Usuario / Correo</th>
                        <th className="py-3 px-4 font-semibold">Rol</th>
                        <th className="py-3 px-4 font-semibold">Firma SHA-256 Token</th>
                        <th className="py-3 px-4 font-semibold">Estado</th>
                        <th className="py-3 px-4 font-semibold text-right">Acción</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {sesionesSSOList.map((s) => (
                        <tr key={s.session_id} className="hover:bg-slate-50/70">
                          <td className="py-3 px-4 font-mono font-bold text-slate-900">{s.session_id}</td>
                          <td className="py-3 px-4">
                            <p className="font-semibold text-slate-800">{s.nombre_completo || s.keycloak_sub}</p>
                            <p className="text-[11px] text-slate-500">{s.email || 'Sesión SSO'}</p>
                          </td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-800 font-semibold text-[11px]">
                              {s.rol}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                            {s.token_sha256.slice(0, 18)}...
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                                s.status === 'ACTIVE_SSO_SESSION'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : 'bg-rose-100 text-rose-800'
                              }`}
                            >
                              {s.status === 'ACTIVE_SSO_SESSION' ? 'ACTIVA' : 'REVOCADA'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            {s.status === 'ACTIVE_SSO_SESSION' && (
                              <button
                                type="button"
                                disabled={pendingAction !== null}
                                onClick={() => handleCerrarSesionSSO(s.session_id)}
                                className="text-rose-600 font-semibold hover:underline disabled:opacity-50"
                              >
                                Revocar
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* FOOTER CORPORATIVO LIMPIO */}
      <footer className="bg-white border-t border-slate-200/80 py-5 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>© 2026 AegisCore Seguros · Plataforma Digital de Pólizas y Coberturas</span>
          </div>
          <span className="text-slate-400">
            Atención 24/7 · Suscripción y Liquidación en Línea
          </span>
        </div>
      </footer>
    </div>
  );
};
