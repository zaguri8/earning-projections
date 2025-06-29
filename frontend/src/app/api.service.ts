import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface ProjectionRequest {
  ticker: string;
  profitMarginTarget?: number;
  yearsToProfitability?: number;
  targetPe?: number;
  bearPe?: number;
  basePe?: number;
  bullPe?: number;
  bearGrowth?: number;
  baseGrowth?: number;
  bullGrowth?: number;
  currentPrice?: number;
  startYear?: number;
  endYear?: number;
  yearsBack?: number;
  currentYear?: number;
  projYears?: number;
  chartingYearsToProfitability?: number;
  useCache?: boolean;
}

export interface ProjectionResponse {
  success: boolean;
  message: string;
  charts: {
    bear: string;  // base64 encoded PNG
    base: string;  // base64 encoded PNG
    bull: string;  // base64 encoded PNG
  };
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5001/api/projections';

  constructor(private http: HttpClient) {}

  getProjections(request: ProjectionRequest): Observable<ProjectionResponse> {
    let params = new HttpParams()
      .set('ticker', request.ticker);

    // Convert percentage values to decimals for the backend
    if (request.profitMarginTarget !== undefined) {
      params = params.set('profit-margin-target', (request.profitMarginTarget / 100).toString());
    }
    if (request.yearsToProfitability !== undefined) {
      params = params.set('years-to-profitability', request.yearsToProfitability.toString());
    }
    if (request.targetPe !== undefined) {
      params = params.set('target-pe', request.targetPe.toString());
    }
    if (request.bearPe !== undefined) {
      params = params.set('bear-pe', request.bearPe.toString());
    }
    if (request.basePe !== undefined) {
      params = params.set('base-pe', request.basePe.toString());
    }
    if (request.bullPe !== undefined) {
      params = params.set('bull-pe', request.bullPe.toString());
    }
    if (request.bearGrowth !== undefined) {
      params = params.set('bear-growth', (request.bearGrowth / 100).toString());
    }
    if (request.baseGrowth !== undefined) {
      params = params.set('base-growth', (request.baseGrowth / 100).toString());
    }
    if (request.bullGrowth !== undefined) {
      params = params.set('bull-growth', (request.bullGrowth / 100).toString());
    }
    if (request.currentPrice !== undefined) {
      params = params.set('current-price', request.currentPrice.toString());
    }
    
    // Add required parameters with defaults if not provided
    params = params.set('start-year', (request.startYear || 2020).toString());
    params = params.set('end-year', (request.endYear || 2024).toString());
    params = params.set('years-back', (request.yearsBack || 5).toString());
    params = params.set('current-year', (request.currentYear || 2025).toString());
    params = params.set('proj-years', (request.projYears || 5).toString());
    params = params.set('charting-years-to-profitability', (request.chartingYearsToProfitability || 3).toString());

    // Add cache option
    if (request.useCache !== undefined) {
      params = params.set('use-cache', request.useCache.toString());
    }

    // Debug logging
    console.log('API Request Parameters:', {
      ticker: request.ticker,
      profitMarginTarget: request.profitMarginTarget,
      yearsToProfitability: request.yearsToProfitability,
      targetPe: request.targetPe,
      bearPe: request.bearPe,
      basePe: request.basePe,
      bullPe: request.bullPe,
      bearGrowth: request.bearGrowth,
      baseGrowth: request.baseGrowth,
      bullGrowth: request.bullGrowth,
      currentPrice: request.currentPrice,
      startYear: request.startYear || 2020,
      endYear: request.endYear || 2024,
      yearsBack: request.yearsBack || 5,
      currentYear: request.currentYear || 2025,
      projYears: request.projYears || 5,
      chartingYearsToProfitability: request.chartingYearsToProfitability || 3,
      useCache: request.useCache
    });

    console.log('API URL with params:', this.apiUrl + '?' + params.toString());

    return this.http.get<ProjectionResponse>(this.apiUrl, { params });
  }
} 