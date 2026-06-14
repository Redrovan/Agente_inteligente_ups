import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-predicciones',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './predicciones.html',
  styleUrl: './predicciones.css'
})
export class PrediccionesComponent implements OnInit {

  private api = inject(ApiService);

  prediccion: any = null;

  ngOnInit(): void {

    this.api
      .getPrediccion()
      .subscribe({

        next: (data: any) => {

          console.log(
            'Predicción recibida'
          );

          console.log(data);

          this.prediccion = data;

        },

        error: (err) => {

          console.error(err);

        }

      });

  }

}