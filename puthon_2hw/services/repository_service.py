"""Service for searching GitHub repositories and exporting to CSV"""

from typing import Any

from aiofile import async_open

from infrastructure.github_client import GitHubClient


class RepositoryService:
    """Service for repository search and CSV export"""

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
        """
        Build GitHub search query with filters

        Args:
            lang: Programming language
            stars_min: Minimum stars
            stars_max: Maximum stars
            forks_min: Minimum forks
            forks_max: Maximum forks

        Returns:
            Formatted query string
        """
        query_parts = []

        # Add language filter
        if lang:
            query_parts.append(f"language:{lang}")

        # Add stars filter
        if stars_max is not None:
            query_parts.append(f"stars:{stars_min}..{stars_max}")
        else:
            query_parts.append(f"stars:>={stars_min}")

        # Add forks filter
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
        """
        Search GitHub repositories with filters

        Args:
            limit: Number of repositories to return
            offset: Number of repositories to skip
            lang: Programming language
            stars_min: Minimum stars
            stars_max: Maximum stars
            forks_min: Minimum forks
            forks_max: Maximum forks

        Returns:
            List of repository dictionaries
        """
        query = self._build_search_query(lang, stars_min, stars_max, forks_min, forks_max)

        all_repos = []
        per_page = 100  # GitHub API max per page
        current_offset = offset

        while len(all_repos) < limit:
            # Calculate page number and items to fetch
            page = (current_offset // per_page) + 1
            items_needed = min(limit - len(all_repos), per_page)

            # Fetch repositories
            result = await self.github_client.search_repositories(
                query=query,
                sort="stars",
                order="desc",
                per_page=items_needed,
                page=page,
            )

            repos = result.get("items", [])
            if not repos:
                break

            # Handle offset within page
            start_idx = current_offset % per_page
            repos_slice = repos[start_idx:]

            all_repos.extend(repos_slice[: limit - len(all_repos)])

            # If we got less than requested, we've reached the end
            if len(repos) < items_needed:
                break

            current_offset += len(repos_slice)

        return all_repos

    async def save_to_csv(
        self,
        repositories: list[dict[str, Any]],
        filename: str,
    ) -> str:
        """
        Save repositories to CSV file

        Args:
            repositories: List of repository dictionaries
            filename: Output filename

        Returns:
            Full path to saved file
        """
        filepath = f"static/{filename}"

        # Prepare data for CSV
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

        # Write to CSV
        async with async_open(filepath, "w", encoding="utf-8") as f:
            if rows:
                fieldnames = list(rows[0].keys())
                content = []

                # Write header
                header = ",".join(fieldnames) + "\n"
                content.append(header)

                # Write rows
                for row in rows:
                    line = ",".join(
                        f'"{str(value).replace(chr(34), chr(34) + chr(34))}"'
                        for value in row.values()
                    )
                    content.append(line + "\n")

                await f.write("".join(content))

        return filepath

