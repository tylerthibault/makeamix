#!/usr/bin/env python3
"""
Test script to validate Flask app can start properly
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, '/app')

try:
    print("Testing Flask app startup...")
    
    # Test import
    print("Importing create_app...")
    from src import create_app
    
    # Test app creation
    print("Creating app...")
    app = create_app()
    
    print("App created successfully!")
    print(f"App name: {app.name}")
    print(f"Debug mode: {app.debug}")
    print(f"Secret key configured: {'SECRET_KEY' in app.config}")
    print(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    
    # Test that app can handle a request
    with app.test_client() as client:
        print("Testing root route...")
        response = client.get('/')
        print(f"Root route status: {response.status_code}")
        
    print("All tests passed!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)