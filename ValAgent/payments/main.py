from fastapi import FastAPI
import payments

app = FastAPI(title="AI Course Payment API (Training)")
app.include_router(payments.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8084, reload=True)
