import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-citas',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './citas.html',
  styleUrl: './citas.css'
})
export class CitasComponent implements OnInit {

  private api = inject(ApiService);

  citas: any[] = [];

  ngOnInit(): void {
    this.cargarCitas();
  }

  cargarCitas() {

    this.api.getCitas().subscribe({

      next: (data: any) => {

        this.citas = data;

      },

      error: (err: any) => {

        console.error(err);

      }

    });

  }

  cancelar(id: number) {

    if (!confirm('¿Cancelar cita?')) {
      return;
    }

    this.api.cancelarCita(id).subscribe({

      next: () => {

        this.cargarCitas();

      },

      error: (err: any) => {

        console.error(err);

      }

    });

  }

  confirmar(id: number) {

  if (
    !confirm(
      '¿Confirmar esta cita?'
    )
  ) {
    return;
  }

  this.api
    .confirmarCita(id)
    .subscribe({

      next: () => {

        alert(
          'Cita confirmada'
        );

        this.cargarCitas();

      },

      error: (err) => {

        console.error(err);

      }

    });

}

}