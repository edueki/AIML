from fastapi import FastAPI
import email_routes

app = FastAPI(title="ValAgent Email API")
app.include_router(email_routes.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)