# app/main.py
from fastapi import FastAPI
import courses  # <-- add this import

app = FastAPI(title="AI Course Enrollment API (Training)")

app.include_router(courses.router)  # <-- add this

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
