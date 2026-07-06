from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from app.db.session import async_get_db
from app.middleware.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.ai_planner import AIPlannerCreateSchema, AIPlannerResumeSchema
from app.db.models import User
from app.services.ai_planner import AIPlannerServices
from app.repositories.ai_planner import AIPlannerRepository
from app.ai.agent.planner_agent import PlannerAgenticWorkflow, PlannerAgent
from app.ai.agent.ai_brain import GrokModel
import math


ai_planner_router = APIRouter(prefix="/ai-planner", tags=["AI Planner"])


# instance
def get_ai_planner_service():
    return AIPlannerServices(AIPlannerRepository())


def get_workflow(request: Request) -> PlannerAgenticWorkflow:
    grok_model = GrokModel()
    planner_agent = PlannerAgent(llm=grok_model)

    return PlannerAgenticWorkflow(
        agent=planner_agent, checkpointer=request.app.state.checkpointer
    )


@ai_planner_router.get("/list", status_code=status.HTTP_200_OK)
async def get_list_ai_plan(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    service: AIPlannerServices = Depends(get_ai_planner_service),
):
    try:
        list, count = await service.get_all_plan(
            db=db, user_id=user.id, offset=offset, limit=limit, search=search
        )
        data = {
            "data": list,
            "total_count": count,
            "total_pages": math.ceil(count / limit),
        }
        return {"success": True, "result": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@ai_planner_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_single_ai_plan(
    id: str,
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    service: AIPlannerServices = Depends(get_ai_planner_service),
):
    try:
        data = await service.get_single_plan(db=db, user_id=user.id, id=id)

        return {"success": True, "result": data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@ai_planner_router.post("/create-plan", status_code=status.HTTP_201_CREATED)
async def create_ai_plan(
    body: AIPlannerCreateSchema,
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    service: AIPlannerServices = Depends(get_ai_planner_service),
    planner_agentic_workflow: PlannerAgenticWorkflow = Depends(get_workflow),
):
    try:
        response = await service.create_plan(
            db=db,
            body=body,
            user=user,
            planner_agentic_workflow=planner_agentic_workflow,
        )
        await db.commit()
        return {"success": True, "result": response}
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@ai_planner_router.post("/resume-plan", status_code=status.HTTP_200_OK)
async def resume_ai_plane(
    body: AIPlannerResumeSchema,
    db: AsyncSession = Depends(async_get_db),
    user: User = Depends(get_current_user),
    service: AIPlannerServices = Depends(get_ai_planner_service),
    planner_agentic_workflow: PlannerAgenticWorkflow = Depends(get_workflow),
):
    try:
        response = await service.resume_plan(
            db=db,
            body=body,
            planner_agentic_workflow=planner_agentic_workflow,
        )
        await db.commit()
        return {"success": True, "result": response}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
