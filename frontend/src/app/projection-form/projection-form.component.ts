import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, ProjectionRequest, ProjectionResponse } from '../api.service';

@Component({
  selector: 'app-projection-form',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="max-w-3xl mx-auto p-6 bg-[#221B2770] backdrop-blur-sm rounded-lg  shadow-2xl border border-gray-700/50">
      <!-- Big Gradient Title -->
      <div class="text-center mb-8">
        <h1 class="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent brightness-150">
          Financial Projections
        </h1>
        <p class="text-gray-300 mt-2 text-lg">Generate and visualize financial projections for any stock</p>
      </div>
      
      <!-- Loading State -->
      <div *ngIf="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h3 class="text-xl font-semibold text-gray-800 mb-2 text-white">Generating Projections...</h3>
        <p class="text-gray-600 mb-4">This process takes approximately 15 seconds</p>
        
        <!-- Progress Steps -->
        <div class="max-w-md mx-auto space-y-3">
          <div class="flex items-center space-x-3">
            <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <span class="text-sm text-gray-400">Fetching financial data</span>
          </div>
          
          <div class="flex items-center space-x-3">
            <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
              </svg>
            </div>
            <span class="text-sm text-gray-400">Calculating projections</span>
          </div>
          
          <div class="flex items-center space-x-3">
            <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center animate-pulse">
              <div class="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <span class="text-sm text-gray-400">Generating charts</span>
          </div>
          
          <div class="flex items-center space-x-3">
            <div class="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center">
              <div class="w-2 h-2 bg-gray-500 rounded-full"></div>
            </div>
            <span class="text-sm text-gray-400">Preparing results</span>
          </div>
        </div>
      </div>

      <!-- Form (hidden when loading) -->
      <form *ngIf="!loading" (ngSubmit)="onSubmit()" class="space-y-6">
        <!-- Basic Info -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Ticker Symbol</label>
            <input 
              type="text" 
              [(ngModel)]="formData.ticker" 
              name="ticker"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
              placeholder="e.g., AAPL, GTLB"
              required
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Current Price ($)</label>
            <input 
              type="number" 
              [(ngModel)]="formData.currentPrice" 
              name="currentPrice"
              class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
              placeholder="e.g., 150.00"
              step="0.01"
            >
          </div>
        </div>

        <!-- Unprofitable Company Parameters -->
        <div class="border-t border-gray-700/30 pt-6">
          <h3 class="text-lg font-semibold text-white mb-4">Unprofitable Company Parameters (Optional)</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Profit Margin Target (%)</label>
              <input 
                type="number" 
                [(ngModel)]="formData.profitMarginTarget" 
                name="profitMarginTarget"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="15"
                step="0.1"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Years to Profitability</label>
              <input 
                type="number" 
                [(ngModel)]="formData.yearsToProfitability" 
                name="yearsToProfitability"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="5"
                min="1"
                max="10"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Target P/E Ratio</label>
              <input 
                type="number" 
                [(ngModel)]="formData.targetPe" 
                name="targetPe"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="25"
                step="0.1"
              >
            </div>
          </div>
        </div>

        <!-- PE Ratios -->
        <div class="border-t border-gray-700/30 pt-6">
          <h3 class="text-lg font-semibold text-white mb-4">P/E Ratios</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Bear P/E</label>
              <input 
                type="number" 
                [(ngModel)]="formData.bearPe" 
                name="bearPe"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="15"
                step="0.1"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Base P/E</label>
              <input 
                type="number" 
                [(ngModel)]="formData.basePe" 
                name="basePe"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="25"
                step="0.1"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Bull P/E</label>
              <input 
                type="number" 
                [(ngModel)]="formData.bullPe" 
                name="bullPe"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="35"
                step="0.1"
              >
            </div>
          </div>
        </div>

        <!-- Growth Rates -->
        <div class="border-t border-gray-700/30 pt-6">
          <h3 class="text-lg font-semibold text-white mb-4">Growth Rates (%)</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Bear Growth</label>
              <input 
                type="number" 
                [(ngModel)]="formData.bearGrowth" 
                name="bearGrowth"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="10"
                step="0.1"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Base Growth</label>
              <input 
                type="number" 
                [(ngModel)]="formData.baseGrowth" 
                name="baseGrowth"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="20"
                step="0.1"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-300 mb-2">Bull Growth</label>
              <input 
                type="number" 
                [(ngModel)]="formData.bullGrowth" 
                name="bullGrowth"
                class="w-full px-3 py-2 bg-gray-800/50 border border-gray-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 backdrop-blur-sm"
                placeholder="30"
                step="0.1"
              >
            </div>
          </div>
        </div>

        <!-- Cache Option -->
        <div class="border-t border-gray-700/30 pt-6">
          <div class="flex items-center">
            <input 
              type="checkbox" 
              [(ngModel)]="formData.useCache" 
              name="useCache"
              id="useCache"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-600 bg-gray-800/50 rounded"
            >
            <label for="useCache" class="ml-2 block text-sm text-gray-300">
              Use cached results (faster, but may not reflect latest data)
            </label>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="border-t border-gray-700/30 pt-6">
          <button 
            type="submit" 
            [disabled]="loading"
            class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-6 rounded-md hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
          >
            <span *ngIf="!loading">Generate Projections</span>
            <span *ngIf="loading">Generating...</span>
          </button>
        </div>
      </form>

      <!-- Error Message -->
      <div *ngIf="error" class="mt-4 p-4 bg-red-900/50 border border-red-500/30 text-red-200 rounded backdrop-blur-sm">
        {{ error }}
      </div>
    </div>
  `
})
export class ProjectionFormComponent {
  @Output() projectionsGenerated = new EventEmitter<{response: ProjectionResponse, ticker: string}>();

  formData: ProjectionRequest = {
    ticker: '',
    profitMarginTarget: undefined,
    yearsToProfitability: undefined,
    targetPe: undefined,
    bearPe: undefined,
    basePe: undefined,
    bullPe: undefined,
    bearGrowth: undefined,
    baseGrowth: undefined,
    bullGrowth: undefined,
    currentPrice: undefined,
    // Required parameters with defaults
    startYear: 2020,
    endYear: 2024,
    yearsBack: 5,
    currentYear: 2025,
    projYears: 5,
    chartingYearsToProfitability: 3,
    // Cache option
    useCache: false
  };

  loading = false;
  error = '';

  constructor(private apiService: ApiService) {}

  onSubmit() {
    if (!this.formData.ticker) {
      this.error = 'Please enter a ticker symbol';
      return;
    }

    this.loading = true;
    this.error = '';

    this.apiService.getProjections(this.formData).subscribe({
      next: (response) => {
        this.loading = false;
        if (response.success) {
          // Emit the response and ticker to parent component
          this.projectionsGenerated.emit({
            response: response,
            ticker: this.formData.ticker
          });
        } else {
          this.error = response.message || 'Failed to generate projections';
        }
      },
      error: (err) => {
        this.loading = false;
        this.error = 'Failed to connect to the API. Please check if the backend server is running.';
        console.error('API Error:', err);
      }
    });
  }
} 