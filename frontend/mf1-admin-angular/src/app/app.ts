import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AgentMonitorService } from './core/services/agent-monitor.service';
import { Observable } from 'rxjs';
import { SystemNotification } from './core/models/agent-monitor.models';

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

  private readonly agentMonitorService = inject(AgentMonitorService);
  readonly notifications$: Observable<SystemNotification[]> = this.agentMonitorService.notifications$;
  readonly unreadCount$: Observable<number> = this.agentMonitorService.unreadCount$;

  ngOnInit(): void {
    const saved = localStorage.getItem('aegis_sidebar_collapsed');
    if (saved !== null) {
      this.isSidebarCollapsed = saved === 'true';
    }

    // Iniciar conexión WebSocket global para alertas de micro-agentes en tiempo real
    this.agentMonitorService.conectarWebSocket().subscribe({
      next: () => {},
      error: (e) => console.warn('[App Shell] Error en canal WS global:', e)
    });
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
