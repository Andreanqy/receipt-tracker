from fastapi import FastAPI

app = FastAPI(title="Receipt Tracker API")

@app.get("/")
def read_root():
    return {"status": "alive", "project": "receipt-tracker"}