from flask import Flask, session, render_template, request, jsonify, redirect, url_for
import os
from datetime import datetime
import json

def create_app():
    app = Flask(__name__)
    app.secret_key = 'dev-key-change-in-production'
    
    # Register blueprints
    from routes.form_steps import form_steps_bp
    from routes.admin_routes import admin_bp
    
    app.register_blueprint(form_steps_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    return app

app = create_app()

@app.route('/')
def home():
    # Initialize session data if not exists
    if 'form_data' not in session:
        session['form_data'] = {
            'current_step': 1,
            'step1': {},
            'step2': {}, 
            'step3': {},
            'step4': {},
            'step5': {}
        }
    return redirect('/step/1')

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Will App is running'}

# FORM DATA ROUTE FOR AUTO-FILL
@app.route('/get-form-data')
def get_form_data():
    """Provide form data for auto-fill functionality"""
    form_data = session.get('form_data', {})
    return jsonify({
        'success': True,
        'form_data': form_data
    })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('storage/generated_documents', exist_ok=True)
    os.makedirs('storage/excel_logs', exist_ok=True)
    os.makedirs('storage/templates', exist_ok=True)
    
    print("🚀 Starting Absolute Wills application...")
    print("📍 Admin portal: http://localhost:5000/admin")
    print("📍 Main app: http://localhost:5000")
    print("📍 Health check: http://localhost:5000/health")
    
    app.run(debug=True, host='0.0.0.0', port=5000)