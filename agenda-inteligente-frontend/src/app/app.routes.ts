import { Routes } from '@angular/router';

import { DashboardComponent } from './pages/dashboard/dashboard';
import { DisponibilidadComponent } from './pages/disponibilidad/disponibilidad';
import { CitasComponent } from './pages/citas/citas';
import { MedicosComponent } from './pages/medicos/medicos';
import { AgendaComponent } from './pages/agenda/agenda';
import { ChatComponent } from './pages/chat/chat';
import { PrediccionesComponent } from './pages/predicciones/predicciones';
import {
  NotificacionesComponent
}
from './pages/notificaciones/notificaciones';

export const routes: Routes = [

  {
    path: '',
    component: DashboardComponent
  },

  {
    path: 'disponibilidad',
    component: DisponibilidadComponent
  },

  {
    path: 'citas',
    component: CitasComponent
  },

  {
    path: 'medicos',
    component: MedicosComponent
  },

  {
    path: 'agenda',
    component: AgendaComponent
  },

  {
    path: 'predicciones',
    component: PrediccionesComponent
  },

  {
    path: 'chat',
    component: ChatComponent
  },

  {
  path: 'notificaciones',
  component: NotificacionesComponent
},

  {
    path: '**',
    redirectTo: ''
  }

];