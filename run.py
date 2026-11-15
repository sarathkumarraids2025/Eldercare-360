
#!/usr/bin/env python
"""
ElderCare 360 - Application Entry Point
Initializes database tables and demo data for local and production servers.
"""

import os
from app import app, seed_database

# Initialize database tables and seed demo data.
# This also runs when Gunicorn imports run.py on Render.
with app.app_context():
    seed_database(app)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ["true", "1"]

    print("=" * 65)
    print("  ELDERCARE 360 HEALTHCARE & MEDICATION PLATFORM")
    print(f"  Access Portal: http://127.0.0.1:{port}")
    print("=" * 65)

    app.run(host="0.0.0.0", port=port, debug=debug)
