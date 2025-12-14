import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    BASE_URL = "https://api.github.com"
    SEARCH_REPOS_ENDPOINT = "/search/repositories"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def search_repositories(
        self,
        query: str,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 30,
        page: int = 1,
    ) -> dict[str, Any]:
        url = f"{self.BASE_URL}{self.SEARCH_REPOS_ENDPOINT}"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(per_page, 100),
            "page": page,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
