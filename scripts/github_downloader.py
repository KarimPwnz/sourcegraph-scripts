import argparse
import asyncio
import logging
import sys
import aiohttp

from aiopath import AsyncPath


class GitHubDownloader:
    def __init__(self, client, output_path, proxy):
        self._client = client
        self.output_path = output_path
        self.proxy = proxy

    @staticmethod
    def _url_to_path(url):
        return url.replace("https://raw.githubusercontent.com/", "")

    async def download(self, url):
        async with self._client.get(url, proxy=self.proxy) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def save(self, url, content):
        path = self.output_path / AsyncPath(self._url_to_path(url))
        await path.parent.mkdir(parents=True, exist_ok=True)
        await path.write_text(content)

    async def download_and_save(self, url, retry_sleep=30):
        logging.info("Downloading %s", url)
        try:
            content = await self.download(url)
        except aiohttp.ClientResponseError as e:
            if e.status == 429:
                logging.warning("Retrying in %s seconds (got 429-ed): %s", retry_sleep, url)
                await asyncio.sleep(retry_sleep)
                return await self.download_and_save(url, retry_sleep * 2)
            logging.error("Status code %s != 200 received: %s", e.status, url)
            return
        except Exception as e:
            logging.exception("Exception occurred while downloading: %s", str(e))
            return
        logging.info("Saving %s", url)
        try:
            await self.save(url, content)
        except Exception as e:
            logging.exception("Exception occurred while saving: %s", str(e))


async def main():
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output", help="Output file path (default: 'out')", default="out"
    )
    parser.add_argument(
        "-l",
        "--limit",
        dest="limit",
        help="Concurrent requests limit (default: 100)",
        default=100,
        type=int,
    )
    parser.add_argument("-p",
        "--proxy",
        dest="proxy",
        help="Proxy to use with each request; proxy domain resolved per request",
        default=None
    )
    args = parser.parse_args()
    conn = aiohttp.TCPConnector(limit=args.limit)
    async with aiohttp.ClientSession(connector=conn) as client:
        downloader = GitHubDownloader(client=client, output_path=args.output, proxy=args.proxy)
        tasks = []
        urls = (l.rstrip("\n") for l in sys.stdin)
        for url in urls:
            tasks.append(downloader.download_and_save(url))
            if len(tasks) == args.limit:
                await asyncio.gather(*tasks)
                tasks = []
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
