from fastapi import FastAPI
import register

app = FastAPI(title="AI Course Enrollment API (Training)")

app.include_router(register.router)

@app.get("/health")
def health():
    return {"status": "ok"}

# 👇 Add this block at the bottom
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
