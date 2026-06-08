from fastapi import APIRouter

health_router = APIRouter(tags=["Health"])


@health_router.get(
    "/health",
    summary="Liveness check",
    responses={
        200: {
            "description": "The service is up and running.",
            "content": {"application/json": {"example": {"status": "ok"}}},
        },
    },
)
async def health() -> dict[str, str]:
    return {"status": "ok"}
