import {
  Component,
  inject,
  ChangeDetectorRef
} from '@angular/core';

import {
  CommonModule
} from '@angular/common';

import {
  FormsModule
} from '@angular/forms';

import {
  ApiService
} from '../../services/api.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class ChatComponent {

  private api = inject(ApiService);

  private cdr = inject(
    ChangeDetectorRef
  );

  mensaje = '';

  mensajes: any[] = [];

  prediccion: any = null;

  enviar() {

    if (!this.mensaje.trim()) {
      return;
    }

    const texto = this.mensaje;

    this.mensajes.push({
      tipo: 'usuario',
      texto
    });

    this.mensajes = [
      ...this.mensajes
    ];

    this.cdr.detectChanges();

    this.mensaje = '';

    this.scrollBottom();

    this.api.enviarMensaje({
      telefono: '593999999999',
      mensaje: texto
    })
    .subscribe({

      next: (resp: any) => {

        console.log(
          'RESPUESTA BACKEND:',
          resp
        );

        // =====================
        // MENSAJE PRINCIPAL
        // =====================

        if (resp.respuesta) {

          this.mensajes.push({
            tipo: 'bot',
            texto: resp.respuesta
          });

        }

        // =====================
        // ESPECIALIDADES
        // =====================

        if (resp.especialidades) {

          this.mensajes.push({
            tipo: 'bot',
            texto:
              'Especialidades disponibles:\n\n' +
              resp.especialidades.join(
                ' | '
              )
          });

        }

        // =====================
        // FECHA
        // =====================

        if (resp.fecha) {

          this.mensajes.push({
            tipo: 'bot',
            texto:
              `Fecha disponible: ${resp.fecha}`
          });

        }

        // =====================
        // HORARIOS
        // =====================

        if (
          resp.horarios &&
          resp.horarios.length > 0
        ) {

          this.mensajes.push({
            tipo: 'horarios',
            horarios: resp.horarios
          });

        }

        // =====================
        // CITAS
        // =====================

        if (resp.citas) {

          this.mensajes.push({
            tipo: 'citas',
            citas: resp.citas
          });

        }

        this.mensajes = [
          ...this.mensajes
        ];

        this.cdr.detectChanges();

        this.scrollBottom();

      },

      error: (err) => {

        console.error(
          'ERROR BACKEND:',
          err
        );

        this.mensajes.push({
          tipo: 'bot',
          texto:
            'Error al comunicarse con el servidor.'
        });

        this.mensajes = [
          ...this.mensajes
        ];

        this.cdr.detectChanges();

        this.scrollBottom();

      }

    });

  }

  // =====================
  // HORARIOS
  // =====================

  seleccionarHorario(
    horario: string
  ) {

    this.mensaje = horario;

    this.enviar();

  }

  // =====================
  // PREDICCION IA
  // =====================

  verPrediccion(
    citaId: number
  ) {

    this.api
      .obtenerPrediccion(citaId)
      .subscribe({

        next: (resp: any) => {

          console.log(
            'PREDICCION:',
            resp
          );

          this.prediccion = resp;

          this.cdr.detectChanges();

        },

        error: (err) => {

          console.error(
            'ERROR PREDICCION:',
            err
          );

        }

      });

  }

  // =====================
  // SCROLL
  // =====================

  scrollBottom() {

    requestAnimationFrame(() => {

      const mensajes =
        document.querySelector(
          '.mensajes'
        );

      if (mensajes) {

        mensajes.scrollTop =
          mensajes.scrollHeight;

      }

    });

  }

}