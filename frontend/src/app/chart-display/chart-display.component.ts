import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chart-display',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div *ngIf="charts" class="max-w-4xl mx-auto p-6">
      <h2 class="text-3xl font-bold text-white mb-6">Financial Projections for {{ ticker }}</h2>
      
      <div class="grid grid-cols-1 gap-8">
        <!-- Bear Scenario -->
        <div class="p-6 border border-gray-700/30">
          <h3 class="text-xl font-semibold text-white mb-4">Bear Scenario</h3>
          <div class="aspect-[16/9] rounded-lg overflow-hidden border border-gray-600/30 bg-black/20 backdrop-blur-sm">
            <img 
              *ngIf="charts.bear" 
              [src]="'data:image/png;base64,' + charts.bear" 
              alt="Bear Scenario Projections"
              class="w-full h-full object-contain mt-4"
            >
            <div *ngIf="!charts.bear" class="flex items-center justify-center h-full text-gray-400">
              No chart available
            </div>
          </div>
          <div class="mt-4 flex justify-center">
            <button 
              *ngIf="charts.bear"
              (click)="downloadChart(charts.bear, ticker + '_bear_scenario.png')"
              class="bg-gray-800/50 text-white px-4 py-2 rounded-md hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-gray-500 border border-gray-600/30 transition-all duration-200"
            >
              Download Bear Chart
            </button>
          </div>
        </div>

        <!-- Base Scenario -->
        <div class="p-6 border border-gray-700/30">
          <h3 class="text-xl font-semibold text-white mb-4">Base Scenario</h3>
          <div class="aspect-[16/9] rounded-lg overflow-hidden border border-gray-600/30 bg-black/20 backdrop-blur-sm">
            <img 
              *ngIf="charts.base" 
              [src]="'data:image/png;base64,' + charts.base" 
              alt="Base Scenario Projections"
              class="w-full h-full object-contain mt-4"
            >
            <div *ngIf="!charts.base" class="flex items-center justify-center h-full text-gray-400">
              No chart available
            </div>
          </div>
          <div class="mt-4 flex justify-center">
            <button 
              *ngIf="charts.base"
              (click)="downloadChart(charts.base, ticker + '_base_scenario.png')"
              class="bg-gray-800/50 text-white px-4 py-2 rounded-md hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-gray-500 border border-gray-600/30 transition-all duration-200"
            >
              Download Base Chart
            </button>
          </div>
        </div>

        <!-- Bull Scenario -->
        <div class="p-6 border border-gray-700/30">
          <h3 class="text-xl font-semibold text-white mb-4">Bull Scenario</h3>
          <div class="aspect-[16/9] rounded-lg overflow-hidden border border-gray-600/30 bg-black/20 backdrop-blur-sm">
            <img 
              *ngIf="charts.bull" 
              [src]="'data:image/png;base64,' + charts.bull" 
              alt="Bull Scenario Projections"
              class="w-full h-full object-contain mt-4"
            >
            <div *ngIf="!charts.bull" class="flex items-center justify-center h-full text-gray-400">
              No chart available
            </div>
          </div>
          <div class="mt-4 flex justify-center">
            <button 
              *ngIf="charts.bull"
              (click)="downloadChart(charts.bull, ticker + '_bull_scenario.png')"
              class="bg-gray-800/50 text-white px-4 py-2 rounded-md hover:bg-gray-700/50 focus:outline-none focus:ring-2 focus:ring-gray-500 border border-gray-600/30 transition-all duration-200"
            >
              Download Bull Chart
            </button>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ChartDisplayComponent {
  @Input() charts: { bear: string; base: string; bull: string } | null = null;
  @Input() ticker: string = '';

  downloadChart(base64Data: string, filename: string) {
    const link = document.createElement('a');
    link.href = 'data:image/png;base64,' + base64Data;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
} 