import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ApiService } from '../../services/api.service';
import { Medico } from '../../models/medico';

@Component({
  selector: 'app-medicos',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './medicos.html',
  styleUrl: './medicos.css'
})
export class MedicosComponent implements OnInit {

  private api = inject(ApiService);

  medicos: Medico[] = [];

  ngOnInit(): void {

    this.api.getMedicos().subscribe({
      next: (data: any) => {
  this.medicos = data as Medico[];
},
      error: (err: any) => {
        console.error(err);
      }
    });

  }
}