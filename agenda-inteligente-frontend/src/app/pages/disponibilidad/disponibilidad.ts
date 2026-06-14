import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-disponibilidad',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './disponibilidad.html',
  styleUrl: './disponibilidad.css'
})
export class DisponibilidadComponent implements OnInit {

  private api = inject(ApiService);

  disponibilidades: any[] = [];

  modoEdicion = false;

  idEditando: number | null = null;

  formulario = {
    medico_id: 1,
    dia_semana: 'MONDAY',
    hora_inicio: '08:00',
    hora_fin: '12:00',
    duracion_cita: 20
  };

  ngOnInit(): void {
    this.cargarDisponibilidad();
  }

  cargarDisponibilidad() {

    this.api
      .getDisponibilidad()
      .subscribe({

        next: (data: any) => {

          this.disponibilidades = data;

        },

        error: (err) => {

          console.error(err);

        }

      });

  }

  editar(disponibilidad: any) {

    this.modoEdicion = true;

    this.idEditando = disponibilidad.id;

    this.formulario = {

      medico_id: disponibilidad.medico_id,

      dia_semana: disponibilidad.dia_semana,

      hora_inicio:
        disponibilidad.hora_inicio.substring(0, 5),

      hora_fin:
        disponibilidad.hora_fin.substring(0, 5),

      duracion_cita:
        disponibilidad.duracion_cita

    };

  }

  desactivar(id: number) {

  if (!confirm('¿Desactivar disponibilidad?')) {
    return;
  }

  this.api
    .desactivarDisponibilidad(id)
    .subscribe({

      next: (resp: any) => {

        alert(
          `Disponibilidad desactivada.\n\n` +
          `Citas reagendadas automáticamente: ${resp.citas_reagendadas}`
        );

        this.cargarDisponibilidad();

      },

      error: (err) => {

        console.error(err);

        alert(
          'Error al desactivar disponibilidad'
        );

      }

    });

}

  guardar() {

    if (this.modoEdicion) {

      this.api
        .editarDisponibilidad(
          this.idEditando!,
          this.formulario
        )
        .subscribe({

          next: () => {

            alert('Disponibilidad actualizada');

            this.modoEdicion = false;

            this.idEditando = null;

            this.cargarDisponibilidad();

          },

          error: (err) => {

            console.error(err);

          }

        });

      return;
    }

    this.api
      .crearDisponibilidad(this.formulario)
      .subscribe({

        next: () => {

          alert('Disponibilidad guardada');

          this.cargarDisponibilidad();

        },

        error: (err) => {

          console.error(err);

        }

      });

  }
}