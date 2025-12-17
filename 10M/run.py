import uvicorn

if __name__ == "__main__":
    print("\n Откройте браузер: http://127.0.0.1:5000")

    uvicorn.run(
        "server:app", host="127.0.0.1", port=5000, reload=True, log_level="info"
    )
