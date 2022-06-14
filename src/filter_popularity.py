import sys
import argparse
import asyncio
import logging
from utils import create_client, setup_logging


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
        async with self._client.get(f"https://api.github.com/users/{username}/repos?type=owner") as resp:
            repos = await resp.json()
            try:
                message = repos.get("message")
                logging.error(
                    "Got error while getting repos of %s: %s", username, message)
                return []
            except AttributeError:
                return repos

    async def is_popular(self, url):
        username = self._gh_url_to_username(url)
        if username in self._usernames:
            return self._usernames[username]
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

    async def print_if_popular(self, url):
        logging.info("Checking %s", url)
        if await self.is_popular(url):
            print(url, flush=True)


async def main():
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", dest="stars", help="Number of minimum stars (default: 100)", default=100, type=int)
    parser.add_argument(
        "-l", dest="limit", help="Concurrent requests limit (default: 20)", default=20, type=int)
    parser.add_argument(
        "-token", dest="token", help="Github token", required=True, type=str)
    args = parser.parse_args()
    async with create_client(request_limit=args.limit, headers={"Authorization": f"Token {args.token}"}) as client:
        checker = PopularityChecker(client=client, min_stars=args.stars)
        urls = (l.rstrip("\n") for l in sys.stdin)
        tasks = []
        for url in urls:
            tasks.append(checker.print_if_popular(url))
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
