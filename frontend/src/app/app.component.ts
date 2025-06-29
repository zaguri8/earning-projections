import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { ProjectionFormComponent } from './projection-form/projection-form.component';
import { ChartDisplayComponent } from './chart-display/chart-display.component';
import { ApiService, ProjectionResponse } from './api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, HttpClientModule, ProjectionFormComponent, ChartDisplayComponent],
  template: `
    <div class="min-h-screen">
      <!-- Header -->
      <header class="bg-black/20 backdrop-blur-sm border-b border-gray-700/30 shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-center py-6">
            <div>
              <h1 class="text-3xl font-bold text-white">Financial Projections</h1>
              <p class="text-gray-300">Generate and visualize financial projections for any stock</p>
            </div>
            <div class="text-right">
              <p class="text-sm text-gray-400">Powered by Python & Angular</p>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <!-- Form Section -->
        <div *ngIf="!projectionResults" class="mb-8">
          <app-projection-form (projectionsGenerated)="onProjectionsGenerated($event)"></app-projection-form>
        </div>

        <!-- Results Section -->
        <div *ngIf="projectionResults">
          <app-chart-display 
            [charts]="projectionResults.charts" 
            [ticker]="currentTicker"
          ></app-chart-display>
          
          <!-- Back Button -->
          <div class="mt-8 text-center">
            <button 
              (click)="resetForm()"
              class="bg-gray-800/50 backdrop-blur-sm text-white px-6 py-3 rounded-md hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-gray-500 border border-gray-600/30 transition-all duration-200"
            >
              Generate New Projections
            </button>
          </div>
        </div>
      </main>

      <!-- Footer -->
      <footer class="bg-black/20 backdrop-blur-sm border-t border-gray-700/30 mt-16">
        <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p class="text-center text-gray-400 text-sm">
            Financial projections are for educational purposes only. Not financial advice.
          </p>
        </div>
      </footer>
    </div>
  `
})
export class AppComponent {
  projectionResults: ProjectionResponse | null = null;
  currentTicker: string = '';

  onProjectionsGenerated(data: {response: ProjectionResponse, ticker: string}) {
    this.projectionResults = data.response;
    this.currentTicker = data.ticker;
  }

  resetForm() {
    this.projectionResults = null;
    this.currentTicker = '';
  }
} 