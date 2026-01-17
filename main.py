from service.bootstrap import app
import uvicorn

if __name__ == "__main__":
    # Entry point for running directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
