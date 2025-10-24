#!/usr/bin/env python3
"""
Startup script with better error handling for debugging
"""
import os
import sys

def main():
    print("=== Flask App Startup Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Check environment variables
    print("\n=== Environment Variables ===")
    print(f"FLASK_APP: {os.environ.get('FLASK_APP', 'Not set')}")
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
    print(f"SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
    
    try:
        print("\n=== Importing Flask App ===")
        from src import create_app
        print("✓ Successfully imported create_app")
        
        print("\n=== Creating App Instance ===")
        app = create_app()
        print("✓ Successfully created app instance")
        
        print(f"App name: {app.name}")
        print(f"App debug: {app.debug}")
        
        return app
        
    except Exception as e:
        print(f"\n❌ ERROR during startup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    app = main()
    print("\n=== Starting Gunicorn ===")
    
    # Import and run gunicorn
    from gunicorn.app.wsgiapp import WSGIApplication
    
    class StandaloneApplication(WSGIApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            for key, value in self.options.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '0.0.0.0:3000',
        'workers': 2,
        'timeout': 120,
        'loglevel': 'info',
        'accesslog': '-',
        'errorlog': '-'
    }
    
    StandaloneApplication(app, options).run()