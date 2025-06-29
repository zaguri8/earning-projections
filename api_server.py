from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import os
import base64
import tempfile
import shutil
from pathlib import Path
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/projections', methods=['GET'])
def get_projections():
    try:
        start_time = time.time()
        print(f"\n=== Starting new projection request ===")
        
        # Get parameters from request
        ticker = request.args.get('ticker', '').upper()
        if not ticker:
            return jsonify({'success': False, 'message': 'Ticker symbol is required'}), 400

        print(f"Processing request for ticker: {ticker}")
        
        # Debug: Print all received parameters
        print("Received parameters:")
        for key, value in request.args.items():
            print(f"  {key}: {value}")

        # Check if user wants to use cache
        use_cache = request.args.get('use-cache', 'false').lower() == 'true'
        print(f"Use cache: {use_cache}")

        # Clear existing cached files for this ticker only if not using cache
        if not use_cache:
            output_dir = Path('charting/output')
            if output_dir.exists():
                cached_files = list(output_dir.glob(f'{ticker}_*_revenue_table.png'))
                for cached_file in cached_files:
                    print(f"Removing cached file: {cached_file}")
                    cached_file.unlink()
        else:
            print("Using cached results - skipping file cleanup")

        # Build command for the projection script - ticker is a global argument
        cmd = [sys.executable, 'main.py', '--ticker', ticker, 'run-all']
        
        # Add optional parameters if provided
        optional_params = [
            ('profit-margin-target', 'profit-margin-target'),
            ('years-to-profitability', 'years-to-profitability'),
            ('target-pe', 'target-pe'),
            ('bear-pe', 'pe-bear'),
            ('base-pe', 'pe-base'),
            ('bull-pe', 'pe-bull'),
            ('bear-growth', 'growth-bear'),
            ('base-growth', 'growth-base'),
            ('bull-growth', 'growth-bull'),
            ('current-price', 'current-price'),
            # Required parameters with defaults
            ('start-year', 'start-year'),
            ('end-year', 'end-year'),
            ('years-back', 'years-back'),
            ('current-year', 'current-year'),
            ('proj-years', 'proj-years'),
            ('charting-years-to-profitability', 'charting-years-to-profitability')
        ]
        
        for param_name, arg_name in optional_params:
            value = request.args.get(param_name)
            if value is not None:
                cmd.extend([f'--{arg_name}', str(value)])
                print(f"  {param_name}: {value}")

        # Check if cached files exist
        output_dir = Path('charting/output')
        cached_files_exist = False
        if output_dir.exists():
            png_files = list(output_dir.glob(f'{ticker}_*_revenue_table.png'))
            cached_files_exist = len(png_files) >= 3  # Need at least bear, base, bull
            print(f"Cached files exist: {cached_files_exist}")

        # Skip Python script execution if using cache and files exist
        if use_cache and cached_files_exist:
            print("Using cached results - skipping Python script execution")
            result = type('MockResult', (), {'returncode': 0, 'stdout': 'Using cached results', 'stderr': ''})()
        else:
            print(f"Executing command: {' '.join(cmd)}")
            print("This will take approximately 15 seconds...")
            
            # Run the projection script
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        execution_time = time.time() - start_time
        print(f"Python script execution completed in {execution_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.returncode != 0:
            error_msg = result.stderr or result.stdout
            print(f"Error running projection script: {error_msg}")
            return jsonify({
                'success': False, 
                'message': f'Failed to generate projections: {error_msg}'
            }), 500

        print(f"Python script stdout: {result.stdout[:500]}...")  # Show first 500 chars

        # Look for generated PNG files
        if not output_dir.exists():
            return jsonify({
                'success': False, 
                'message': 'Output directory not found'
            }), 500

        # Wait a moment for files to be written
        time.sleep(1)

        # Find the generated PNG files for this specific ticker
        png_files = list(output_dir.glob(f'{ticker}_*_revenue_table.png'))
        if not png_files:
            return jsonify({
                'success': False, 
                'message': f'No chart files generated for {ticker}'
            }), 500

        print(f"Found PNG files: {[f.name for f in png_files]}")

        # Convert PNG files to base64
        charts = {}
        for png_file in png_files:
            if 'bear' in png_file.name.lower():
                charts['bear'] = encode_image_to_base64(png_file)
                print(f"Added bear chart: {png_file.name}")
            elif 'base' in png_file.name.lower():
                charts['base'] = encode_image_to_base64(png_file)
                print(f"Added base chart: {png_file.name}")
            elif 'bull' in png_file.name.lower():
                charts['bull'] = encode_image_to_base64(png_file)
                print(f"Added bull chart: {png_file.name}")

        print(f"Charts found: {list(charts.keys())}")
        total_time = time.time() - start_time
        print(f"Total API response time: {total_time:.2f} seconds")
        print("=== Request completed ===\n")

        return jsonify({
            'success': True,
            'message': f'Projections generated successfully for {ticker} in {total_time:.2f} seconds',
            'charts': charts
        })

    except Exception as e:
        print(f"Error in API: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Internal server error: {str(e)}'
        }), 500

def encode_image_to_base64(image_path):
    """Convert an image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image {image_path}: {str(e)}")
        return None

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API server is running'})

if __name__ == '__main__':
    print("Starting Financial Projections API Server...")
    print("API will be available at: http://localhost:5001")
    print("Health check: http://localhost:5001/api/health")
    app.run(debug=True, host='0.0.0.0', port=5001) 