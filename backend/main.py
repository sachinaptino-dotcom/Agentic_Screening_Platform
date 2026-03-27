import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth_router import router as auth_router
from routers.jobs_router import router as jobs_router
from routers.upload_router import router as upload_router
from vector_store import load_index


ATS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ATS_ROOT not in sys.path:
    sys.path.append(ATS_ROOT)

app = FastAPI(title="Local ATS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    load_index()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(jobs_router)
