from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth import auth_router
from app.api.v1.user import user_router
from app.api.v1.discussion import discussion_router
from app.api.v1.worksheet import worksheet_router
from app.api.v1.paper import paper_router
from app.api.v1.doc import doc_router
from app.api.v1.integration import integration_router
from app.api.v1.ai_planner import ai_planner_router
from starlette.middleware.sessions import SessionMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager
from app.config import settings


# -------------------------------
# Life span CONFIGURATION
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with AsyncPostgresSaver.from_conn_string(
        "postgresql://postgres:admin54321@localhost:5432/edu_db"
    ) as saver:
        await saver.setup()
        app.state.checkpointer = saver
        yield


# -------------------------------
# CORS CONFIGURATION
# -------------------------------
origins = [
    "http://localhost:5173",  # Vite default
    "http://127.0.0.1:5173",
    "https://your-production-domain.com",
]


app = FastAPI(
    title="Edu-Talks",
    description="AI base discussion and uploading documents",
    version="v1",
    contact={"name": "Abdul Basit", "email": "basit9498@gmail.com"},
    lifespan=lifespan,
)

app.mount("/public/doc", StaticFiles(directory="app/public/doc"), name="documents")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE
    allow_headers=["*"],  # Authorization, Content-Type
)
app.add_middleware(
    SessionMiddleware,
    secret_key="SUPER_SECRET_KEY_CHANGE_THIS",
    max_age=300,  # 5 minutes
    same_site="lax",
    # https_only=True,  # production
)


@app.get("/health")
def root():
    return {"message": "API working"}


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(discussion_router)
app.include_router(worksheet_router)
app.include_router(paper_router)
app.include_router(doc_router)
app.include_router(integration_router)
app.include_router(ai_planner_router)
