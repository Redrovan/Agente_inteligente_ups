import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-notificaciones',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './notificaciones.html',
  styleUrl: './notificaciones.css'
})
export class NotificacionesComponent
implements OnInit {

  private api = inject(ApiService);

  notificaciones: any[] = [];

  ngOnInit() {

    this.cargar();

  }

  cargar() {

    this.api
      .getNotificaciones()
      .subscribe({

        next: (resp: any) => {

          this.notificaciones = resp;

        },

        error: (err) => {

          console.error(err);

        }

      });

  }

}