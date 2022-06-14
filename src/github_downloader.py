from utils import create_client, setup_logging
from aiopath import AsyncPath
import asyncio
import sys
import logging
import argparse


class GitHubDownloader:
    def __init__(self, client, output_path):
        self._client = client
        self.output_path = output_path

    @staticmethod
    def _url_to_path(url):
        return url.replace("https://raw.githubusercontent.com/", "")

    async def download(self, url):
        async with self._client.get(url) as resp:
            return await resp.text()

    async def save(self, url, content):
        path = self.output_path / AsyncPath(self._url_to_path(url))
        await path.parent.mkdir(parents=True, exist_ok=True)
        await path.write_text(content)

    async def download_and_save(self, url):
        logging.info("Downloading %s", url)
        try:
            content = await self.download(url)
        except Exception as e:
            logging.exception(
                "Exception occurred while downloading: %s", str(e))
            return
        logging.info("Saving %s", url)
        try:
            await self.save(url, content)
        except Exception as e:
            logging.exception("Exception occurred while saving: %s", str(e))


async def main():
    setup_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output", help="Output file path", default="out")
    parser.add_argument(
        "-l", dest="limit", help="Concurrent requests limit (default: 100)", default=100, type=int)
    args = parser.parse_args()
    async with create_client(request_limit=args.limit) as client:
        downloader = GitHubDownloader(client=client, output_path=args.output)
        tasks = []
        urls = (l.rstrip("\n") for l in sys.stdin)
        for url in urls:
            tasks.append(downloader.download_and_save(url))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
