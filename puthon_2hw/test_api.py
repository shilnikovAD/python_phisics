"""
Test script for GitHub Repository Search API
"""

import asyncio

import httpx


async def test_api():
    """Test API endpoints"""

    base_url = "http://localhost:8001"

    async with httpx.AsyncClient() as client:
        # Test root endpoint
        print("Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        # Test search endpoint with Python repositories
        print("Testing search endpoint with Python repositories...")
        params = {
            "limit": 10,
            "offset": 0,
            "lang": "Python",
            "stars_min": 1000,
        }
        response = await client.get(f"{base_url}/api/search", params=params)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")

        # Check if CSV file was created
        import os

        csv_file = "static/repositories_Python_10_0.csv"
        if os.path.exists(csv_file):
            print(f"CSV file created successfully: {csv_file}")
            with open(csv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                print(f"File contains {len(lines)} lines (including header)")
                if len(lines) > 0:
                    print(f"Header: {lines[0].strip()}")
        else:
            print(f"CSV file not found: {csv_file}")


if __name__ == "__main__":
    asyncio.run(test_api())

