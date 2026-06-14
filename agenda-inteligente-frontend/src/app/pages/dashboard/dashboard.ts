import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  BaseChartDirective
} from 'ng2-charts';

import {
  Chart,
  PieController,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

import { ApiService } from '../../services/api.service';

Chart.register(
  PieController,
  ArcElement,
  Tooltip,
  Legend
);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    BaseChartDirective
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {

  private api = inject(ApiService);

  dashboard: any = null;

  pieChartLabels = [
    'Programadas',
    'Canceladas',
    'Reagendadas'
  ];

  pieChartData = {
    labels: this.pieChartLabels,
    datasets: [
      {
        data: [0, 0, 0],
        backgroundColor: [
          '#22c55e',
          '#ef4444',
          '#3b82f6'
        ]
      }
    ]
  };

  ngOnInit(): void {

    this.api.getDashboard().subscribe({

      next: (data: any) => {

        console.log('Dashboard cargado');
        console.log(data);

        this.dashboard = data;

        this.pieChartData = {
          labels: this.pieChartLabels,
          datasets: [
            {
              data: [
                data.citas_programadas,
                data.citas_canceladas,
                data.citas_reagendadas
              ],
              backgroundColor: [
                '#22c55e',
                '#ef4444',
                '#3b82f6'
              ]
            }
          ]
        };

      },

      error: (err) => {

        console.error(
          'Error dashboard',
          err
        );

      }

    });

  }

}