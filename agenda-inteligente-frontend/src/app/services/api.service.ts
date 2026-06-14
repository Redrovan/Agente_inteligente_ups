import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private api = environment.apiUrl;

  constructor(
    private http: HttpClient
  ) {}

  getDashboard() {
    return this.http.get(`${this.api}/dashboard`);
  }

  getCitas() {
    return this.http.get(`${this.api}/citas`);
  }

  getMedicos() {
    return this.http.get(`${this.api}/medicos`);
  }

  getDisponibilidad() {
    return this.http.get(
      `${this.api}/configuracion/disponibilidad`
    );
  }

  crearDisponibilidad(data: any) {
    return this.http.post(
      `${this.api}/configuracion/disponibilidad`,
      data
    );
  }

  editarDisponibilidad(
    id: number,
    data: any
  ) {
    return this.http.put(
      `${this.api}/configuracion/disponibilidad/${id}`,
      data
    );
  }

  desactivarDisponibilidad(id: number) {
    return this.http.put(
      `${this.api}/configuracion/disponibilidad/${id}/desactivar`,
      {}
    );
  }

  getAgendaSemanal() {
    return this.http.get(
      `${this.api}/agenda-semanal`
    );
  }

  cancelarCita(id: number) {
    return this.http.put(
      `${this.api}/citas/${id}/cancelar`,
      {}
    );
  }

  enviarMensaje(data: any) {
    return this.http.post(
      `${this.api}/chat`,
      data
    );
  }

  getPrediccion() {
    return this.http.get(
      `${this.api}/predicciones/demanda`
    );
  }

  obtenerPrediccion(
    citaId: number
  ) {
    return this.http.get(
      `${this.api}/predicciones/espera/${citaId}`
    );
  }

  obtenerConfiguracionAgenda() {
  return this.http.get(
    `${this.api}/configuracion-agenda`
  );
}

crearConfiguracionAgenda(data: any) {
  return this.http.post(
    `${this.api}/configuracion-agenda`,
    data
  );
}

getNotificaciones() {

  return this.http.get(
    `${this.api}/notificaciones`
  );

}


confirmarCita(id: number) {

  return this.http.put(
    `${this.api}/citas/${id}/confirmar`,
    {}
  );

}

getDashboardEjecutivo() {
  return this.http.get(
    `${this.api}/dashboard-ejecutivo`
  );
}

}