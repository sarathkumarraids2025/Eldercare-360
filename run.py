#!/usr/bin/env python
"""
ElderCare 360 - Production Entrypoint
Launches the Flask WSGI Application with automatic database initialization.
"""

import os
from app import app, seed_database

if __name__ == '__main__':
    with app.app_context():
        seed_database(app)
        
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1']
    
    print("=" * 65)
    print("  🏥 ELDERCARE 360 HEALTHCARE & MEDICATION PLATFORM")
    print(f"  Access Portal: http://127.0.0.1:{port}")
    print("  Demo Logins:   ramalingam (Senior) | nurse_anitha (Caregiver)")
    print("                 vijay_son (Family)   | dr_subramanian (Doctor)")
    print("=" * 65)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
