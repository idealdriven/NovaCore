from fastapi import FastAPI
from database import engine
from api import owners, brands, services, conversations, strategic_plans, execution_logs, tasks, memories

app = FastAPI()

# Include the API routers
app.include_router(owners.router, prefix="/owners", tags=["owners"])
app.include_router(brands.router, prefix="/brands", tags=["brands"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
app.include_router(strategic_plans.router, prefix="/strategic-plans", tags=["strategic plans"])
app.include_router(execution_logs.router, prefix="/execution-logs", tags=["execution logs"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(memories.router, prefix="/memories", tags=["memories"])

@app.on_event("startup")
async def startup():
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Atlas API!"}
