from fastapi import FastAPI
import enrollment

app = FastAPI(title="AI Course Enrollment API (Training)")
app.include_router(enrollment.router)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8083, reload=True)
