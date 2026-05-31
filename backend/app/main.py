from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.jobs import router as jobs_router

app = FastAPI(
    title="CareerPilot API",
    version="1.0.0",
    docs_url="/docs",
)
from app.routes.router import api_router

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])


@app.get("/health")
def health():
    return {"status": "ok"}
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Backend running"}
