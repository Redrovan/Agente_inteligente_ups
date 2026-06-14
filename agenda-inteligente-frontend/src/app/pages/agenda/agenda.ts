import {
  Component,
  OnInit,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-agenda',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agenda.html',
  styleUrl: './agenda.css'
})
export class AgendaComponent implements OnInit {

  private api = inject(ApiService);

  agenda: any = {};

  dias: string[] = [];

  ngOnInit(): void {

    console.log('AGENDA COMPONENT CARGADO');

    this.api
      .getAgendaSemanal()
      .subscribe({

        next: (data: any) => {

          console.log('AGENDA RECIBIDA');
          console.log(data);

          this.agenda = data;

          this.dias = Object.keys(data);

          console.log('DIAS');
          console.log(this.dias);

        },

        error: (err: any) => {

          console.error('ERROR AGENDA');
          console.error(err);

        }

      });

  }

}