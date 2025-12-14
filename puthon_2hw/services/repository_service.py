from typing import Any

import aiofiles

from infrastructure.github_client import GitHubClient


class RepositoryService:
    def __init__(self):
        self.github_client = GitHubClient()

    def _build_search_query(
        self,
        lang: str | None = None,
        stars_min: int = 0,
        stars_max: int | None = None,
        forks_min: int = 0,
        forks_max: int | None = None,
    ) -> str:
        query_parts = []
        if lang:
            query_parts.append(f"language:{lang}")
        if stars_max is not None:
            query_parts.append(f"stars:{stars_min}..{stars_max}")
        else:
            query_parts.append(f"stars:>={stars_min}")
        if forks_max is not None:
            query_parts.append(f"forks:{forks_min}..{forks_max}")
        else:
            query_parts.append(f"forks:>={forks_min}")
        return " ".join(query_parts)

    async def search_repositories(
        self,
        limit: int,
        offset: int = 0,
        lang: str | None = None,
        stars_min: int = 0,
        stars_max: int | None = None,
        forks_min: int = 0,
        forks_max: int | None = None,
    ) -> list[dict[str, Any]]:
        query = self._build_search_query(lang, stars_min, stars_max, forks_min, forks_max)
        all_repos = []
        per_page = 100
        current_offset = offset
        while len(all_repos) < limit:
            page = current_offset // per_page + 1
            items_needed = min(limit - len(all_repos), per_page)
            result = await self.github_client.search_repositories(
                query=query, sort="stars", order="desc", per_page=items_needed, page=page
            )
            repos = result.get("items", [])
            if not repos:
                break
            start_idx = current_offset % per_page
            repos_slice = repos[start_idx:]
            all_repos.extend(repos_slice[: limit - len(all_repos)])
            if len(repos) < items_needed:
                break
            current_offset += len(repos_slice)
        return all_repos

    async def save_to_csv(self, repositories: list[dict[str, Any]], filename: str) -> str:
        filepath = f"static/{filename}"
        rows = []
        for repo in repositories:
            rows.append(
                {
                    "name": repo.get("name", ""),
                    "owner": repo.get("owner", {}).get("login", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language", ""),
                    "url": repo.get("html_url", ""),
                    "description": repo.get("description", ""),
                    "created_at": repo.get("created_at", ""),
                    "updated_at": repo.get("updated_at", ""),
                }
            )
        async with aiofiles.open(filepath, "w", encoding="utf-8", newline="") as f:
            if rows:
                fieldnames = list(rows[0].keys())
                header = ",".join(fieldnames) + "\n"
                await f.write(header)
                for row in rows:
                    line = ",".join(
                        f'"{str(value).replace(chr(34), chr(34) + chr(34))}"'
                        for value in row.values()
                    )
                    await f.write(line + "\n")
        return filepath
