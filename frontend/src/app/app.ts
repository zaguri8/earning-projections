import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ProjectionResponse } from './api.service';
import { ChartDisplayComponent } from './chart-display/chart-display.component';
import { ProjectionFormComponent } from './projection-form/projection-form.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ProjectionFormComponent, ChartDisplayComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected title = 'frontend';

  protected chartData: { bear: string; base: string; bull: string } | null = null;
  protected ticker = signal<string>('AAPL');

  protected onProjectionsGenerated(data: {response: ProjectionResponse, ticker: string}) {
    this.chartData = data.response.charts;
    this.ticker.set(data.ticker);
  }
}
