from fastapi import FastAPI

app = FastAPI(title="QA Site Check")

@app.get("/health")
def health_check():
    return {"status": "ok"}
