import aiohttp
import argparse
import asyncio
import logging
import sys


class PopularityChecker:
    def __init__(self, client, min_stars):
        self._client = client
        self.min_stars = min_stars
        self._usernames = {}

    @staticmethod
    def _gh_url_to_username(url):
        # https://raw.githubusercontent.com/USERNAME/...
        return url.split("/")[3]

    async def get_repos(self, username):
        async with self._client.get(
            f"https://api.github.com/users/{username}/repos?type=owner"
        ) as resp:
            repos = await resp.json()
            try:
                message = repos.get("message")
                logging.error(
                    "Got error while getting repos of %s: %s", username, message
                )
                return []
            except AttributeError:
                return repos

    async def check_popularity(self, username):
        logging.info("Getting repos of %s", username)
        try:
            repos = await self.get_repos(username)
        except Exception as e:
            logging.exception("Exception occurred %s", str(e))
            return False
        for repo in repos:
            if repo.get("stargazers_count", -1) >= self.min_stars:
                self._usernames[username] = True
                return True
        self._usernames[username] = False
        return False


    async def is_popular(self, query):
        if query.startswith("https://raw.githubusercontent.com/"):
            username = self._gh_url_to_username(query)
        else:
            username = query
        if username not in self._usernames:
            self._usernames[username] = asyncio.ensure_future(self.check_popularity(username))
        return await self._usernames[username]

    async def print_if_popular(self, query):
        logging.info("Checking %s", query)
        if await self.is_popular(query):
            print(query, flush=True)


async def main():
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        dest="stars",
        help="Number of minimum stars (default: 100)",
        default=100,
        type=int,
    )
    parser.add_argument(
        "-l",
        dest="limit",
        help="Concurrent requests limit (default: 20)",
        default=20,
        type=int
    )
    parser.add_argument(
        "-token", dest="token", help="Github token", required=False, type=str
    )
    args = parser.parse_args()
    headers = {}
    if args.token:
        headers["Authorization"] = f"Token {args.token}"
    conn = aiohttp.TCPConnector(limit=args.limit)
    async with aiohttp.ClientSession(connector=conn) as client:
        checker = PopularityChecker(client=client, min_stars=args.stars)
        queries = (l.rstrip("\n") for l in sys.stdin)
        tasks = []
        for query in queries:
            tasks.append(checker.print_if_popular(query))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
