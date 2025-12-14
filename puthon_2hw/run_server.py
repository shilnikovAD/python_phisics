import sys
sys.path.insert(0, '.')

try:
    print("Importing main module...")
    from main import app
    print("✓ Main module imported successfully")

    print("\nImporting uvicorn...")
    import uvicorn
    print("✓ Uvicorn imported successfully")

    print("\nStarting server on http://127.0.0.1:8001")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)

    uvicorn.run(app, host="127.0.0.1", port=8001)

except Exception as e:
    print(f"\n Error: {e}")
    import traceback
    traceback.print_exc()

