from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from services.repository_service import RepositoryService

router = APIRouter()


@router.get("/search")
async def search_repositories(
    limit: Annotated[int, Query(description="Number of repositories to return", ge=1, le=1000)],
    offset: Annotated[int, Query(description="Number of repositories to skip", ge=0)] = 0,
    lang: Annotated[str | None, Query(description="Programming language")] = None,
    stars_min: Annotated[int, Query(description="Minimum stars", ge=0)] = 0,
    stars_max: Annotated[int | None, Query(description="Maximum stars", ge=0)] = None,
    forks_min: Annotated[int, Query(description="Minimum forks", ge=0)] = 0,
    forks_max: Annotated[int | None, Query(description="Maximum forks", ge=0)] = None,
):
    try:
        if stars_max is not None and stars_max < stars_min:
            raise HTTPException(
                status_code=400, detail="stars_max must be greater than or equal to stars_min"
            )
        if forks_max is not None and forks_max < forks_min:
            raise HTTPException(
                status_code=400, detail="forks_max must be greater than or equal to forks_min"
            )
        service = RepositoryService()
        repositories = await service.search_repositories(
            limit=limit,
            offset=offset,
            lang=lang,
            stars_min=stars_min,
            stars_max=stars_max,
            forks_min=forks_min,
            forks_max=forks_max,
        )
        lang_str = lang if lang else "all"
        filename = f"repositories_{lang_str}_{limit}_{offset}.csv"
        filepath = await service.save_to_csv(repositories, filename)
        return JSONResponse(
            content={
                "status": "success",
                "message": "Repositories exported to CSV",
                "file": filepath,
                "count": len(repositories),
                "filters": {
                    "limit": limit,
                    "offset": offset,
                    "language": lang,
                    "stars_min": stars_min,
                    "stars_max": stars_max,
                    "forks_min": forks_min,
                    "forks_max": forks_max,
                },
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
