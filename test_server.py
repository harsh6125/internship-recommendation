# test_server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# A minimal app to test the connection
app = FastAPI()

# Add CORS so the browser can talk to it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    # If this works, it will send back {"Hello": "World"}
    return {"Hello": "World"}