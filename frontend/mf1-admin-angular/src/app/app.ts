import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AgentMonitorService } from './core/services/agent-monitor.service';
import { Observable } from 'rxjs';
import { SystemNotification } from './core/models/agent-monitor.models';

export interface SsoUserContext {
  nombre: string;
  email: string;
  rol: string;
  sessionId: string;
  iniciales: string;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  title = 'AegisCore AI — Portal ERP & BI Actuarial';
  isSidebarCollapsed = false;
  isNotificationMenuOpen = false;

  isAuthenticated = false;
  authChecked = false;

  ssoUser: SsoUserContext = {
    nombre: '',
    email: '',
    rol: '',
    sessionId: '',
    iniciales: ''
  };

  private readonly router = inject(Router);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly agentMonitorService = inject(AgentMonitorService);
  readonly notifications$: Observable<SystemNotification[]> = this.agentMonitorService.notifications$;
  readonly unreadCount$: Observable<number> = this.agentMonitorService.unreadCount$;

  ngOnInit(): void {
    const saved = localStorage.getItem('aegis_sidebar_collapsed');
    if (saved !== null) {
      this.isSidebarCollapsed = saved === 'true';
    }

    this.sincronizarContextoSSO();

    // Iniciar conexión WebSocket global para alertas de micro-agentes en tiempo real
    this.agentMonitorService.conectarWebSocket().subscribe({
      next: () => {},
      error: (e) => console.warn('[App Shell] Error en canal WS global:', e)
    });
  }

  get ms1BaseUrl(): string {
    if (typeof window !== 'undefined' && (window as any).__AEGIS_MS1_URL) {
      return (window as any).__AEGIS_MS1_URL;
    }
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    return isLocal ? 'http://localhost:8001' : 'https://aegiscore-ms1-polizas-jskh4rw62q-uc.a.run.app';
  }

  get ssoShellUrl(): string {
    if (typeof window !== 'undefined' && (window as any).__AEGIS_SSO_URL) {
      return (window as any).__AEGIS_SSO_URL;
    }
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    return isLocal ? 'http://localhost:8080' : 'https://aegiscore-mf2-clientes-302263088715.s3.us-east-2.amazonaws.com/sso.html';
  }

  get reactPwaUrl(): string {
    if (typeof window !== 'undefined' && (window as any).__AEGIS_REACT_URL) {
      return (window as any).__AEGIS_REACT_URL;
    }
    const isLocal = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
    return isLocal ? 'http://localhost:3000' : 'https://aegiscore-mf2-clientes-302263088715.s3.us-east-2.amazonaws.com/index.html';
  }

  volverAlHubPrincipal(): void {
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
        window.top.location.href = this.ssoShellUrl;
      } else {
        window.location.href = this.ssoShellUrl;
      }
    }
  }

  private sincronizarContextoSSO(): void {
    if (typeof window === 'undefined') return;

    // Timeout de seguridad: nunca dejar la pantalla bloqueada en "Verificando..." más de 2.5s
    const timeoutSeguridad = setTimeout(() => {
      if (!this.authChecked) {
        this.authChecked = true;
        this.cdr.detectChanges();
      }
    }, 2500);

    const params = new URLSearchParams(window.location.search);
    const emailParam = params.get('sso_email') || params.get('email');
    const rolParam = params.get('sso_rol') || params.get('rol');
    const nameParam = params.get('sso_name') || params.get('nombre');
    const sessionParam = params.get('sso_session') || params.get('session_id');

    if (emailParam) {
      clearTimeout(timeoutSeguridad);
      this.isAuthenticated = true;
      this.authChecked = true;
      this.establecerUsuarioSSO(
        emailParam,
        rolParam || 'ACTUARIO',
        nameParam,
        sessionParam
      );
      this.cdr.detectChanges();
      return;
    }

    // Verificar si ya existe una sesión guardada localmente para acceso instantáneo sin parpadeo
    const guardado = localStorage.getItem('aegiscore_sso_session_angular');
    if (guardado) {
      try {
        const parsed = JSON.parse(guardado) as SsoUserContext;
        if (parsed && parsed.email) {
          clearTimeout(timeoutSeguridad);
          this.isAuthenticated = true;
          this.authChecked = true;
          this.ssoUser = parsed;
          this.cdr.detectChanges();
          return;
        }
      } catch {}
    }

    // Consultar MS1 DynamoDB por la sesión autoritativa activa en el cluster con límite de tiempo
    const fetchOptions: RequestInit = {};
    if (typeof AbortSignal !== 'undefined' && 'timeout' in AbortSignal) {
      fetchOptions.signal = AbortSignal.timeout(3000);
    }

    fetch(`${this.ms1BaseUrl}/api/v1/auth/sso-sessions`, fetchOptions)
      .then((res) => (res.ok ? res.json() : null))
      .then((data: { authenticated?: boolean; active_session?: { email?: string; rol?: string; nombre_completo?: string; session_id?: string } } | null) => {
        clearTimeout(timeoutSeguridad);
        this.authChecked = true;
        if (data && data.authenticated && data.active_session) {
          this.isAuthenticated = true;
          const u = data.active_session;
          this.establecerUsuarioSSO(
            u.email || 'actuario@aegiscore.com',
            u.rol || 'ACTUARIO',
            u.nombre_completo,
            u.session_id
          );
        } else {
          this.isAuthenticated = false;
          localStorage.removeItem('aegiscore_sso_session_angular');
          if (window.self === window.top) {
            setTimeout(() => {
              window.location.href = this.ssoShellUrl;
            }, 1800);
          }
        }
        this.cdr.detectChanges();
      })
      .catch(() => {
        clearTimeout(timeoutSeguridad);
        this.authChecked = true;
        // Modo Resiliente: en caso de timeout de red, activar sesión por defecto para evitar pantalla congelada
        this.isAuthenticated = true;
        this.establecerUsuarioSSO(
          'actuario@aegiscore.com',
          'ACTUARIO',
          'Lic. Mariana Vargas',
          'sso-sess-resiliente'
        );
        this.cdr.detectChanges();
      });
  }

  private establecerUsuarioSSO(
    email: string,
    rol: string,
    nombre?: string | null,
    sessionId?: string | null
  ): void {
    let resolvedName = nombre;
    if (!resolvedName || resolvedName.trim() === '') {
      if (email.includes('carlos')) resolvedName = 'Carlos Mendoza Roca';
      else if (email.includes('admin')) resolvedName = 'Administrador General';
      else if (email.includes('perito')) resolvedName = 'Ing. Roberto Paz';
      else if (email.includes('actuario')) resolvedName = 'Lic. Mariana Vargas';
      else resolvedName = email.split('@')[0];
    }

    const iniciales = resolvedName
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((w) => w[0].toUpperCase())
      .join('');

    const upperRol = rol.toUpperCase();
    this.ssoUser = {
      email,
      rol: upperRol,
      nombre: resolvedName,
      sessionId: sessionId || `sso-sess-${upperRol.toLowerCase()}`,
      iniciales: iniciales || 'AC'
    };

    try {
      localStorage.setItem('aegiscore_sso_session_angular', JSON.stringify(this.ssoUser));
    } catch {}

    // Enrutamiento inteligente por Rol
    if (upperRol === 'PERITO') {
      const currentUrl = this.router.url;
      if (currentUrl === '/' || currentUrl === '/autonomous-agent-monitor' || currentUrl === '/executive-kpi-dashboard' || currentUrl === '/actuarial-dashboard') {
        this.router.navigate(['/ai-damage-inspector']);
      }
    } else if (upperRol === 'ACTUARIO') {
      const currentUrl = this.router.url;
      if (currentUrl === '/' || currentUrl === '/autonomous-agent-monitor') {
        this.router.navigate(['/executive-kpi-dashboard']);
      }
    }
  }

  cerrarSesion(): void {
    fetch(`${this.ms1BaseUrl}/api/v1/auth/sso-logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: 'ALL' })
    }).finally(() => {
      localStorage.removeItem('aegiscore_sso_session_angular');
      this.isAuthenticated = false;
      window.location.href = this.ssoShellUrl;
    });
  }

  // Comprobaciones RBAC para los ítems del menú lateral
  canAccessActuarial(): boolean {
    return this.ssoUser.rol === 'ACTUARIO' || this.ssoUser.rol === 'ADMIN';
  }

  canAccessExecutiveKpi(): boolean {
    return this.ssoUser.rol === 'ACTUARIO' || this.ssoUser.rol === 'ADMIN';
  }

  canAccessAiDamage(): boolean {
    return this.ssoUser.rol === 'PERITO' || this.ssoUser.rol === 'ADMIN';
  }

  canAccessFraud(): boolean {
    return this.ssoUser.rol === 'ACTUARIO' || this.ssoUser.rol === 'ADMIN';
  }

  canAccessAgentMonitor(): boolean {
    return this.ssoUser.rol === 'ADMIN';
  }

  canAccessVoiceMcp(): boolean {
    return this.ssoUser.rol === 'PERITO' || this.ssoUser.rol === 'ACTUARIO' || this.ssoUser.rol === 'ADMIN';
  }

  toggleSidebar(): void {
    this.isSidebarCollapsed = !this.isSidebarCollapsed;
    localStorage.setItem('aegis_sidebar_collapsed', String(this.isSidebarCollapsed));
  }

  toggleNotificationMenu(): void {
    this.isNotificationMenuOpen = !this.isNotificationMenuOpen;
  }

  markAllAsRead(): void {
    this.agentMonitorService.markAllAsRead();
  }

  markAsRead(id: string): void {
    this.agentMonitorService.markAsRead(id);
  }

  clearAllNotifications(): void {
    this.agentMonitorService.clearAllNotifications();
  }
}
