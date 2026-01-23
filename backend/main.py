from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Backend health route
@app.get("/health")
def health():
    return {"health": "healthy"}

# Game stats route
@app.get("/stats")
def stats():
    return{"Home score": "125"}