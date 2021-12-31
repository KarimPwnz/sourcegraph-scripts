import concurrent.futures
import pandas as pd
import argparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path


def gh_url_to_raw(url):
    # Marcus Fedarko (fedarko), gh_url_to_raw_gh_url.py, https://gist.github.com/fedarko/4fc177cff9084b9e325dcbe954547edc
    return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")


def gh_url_to_filepath(url):
    return url.replace("https://github.com/", "")


def fetch_url(http, url):
    raw_url = gh_url_to_raw(url)
    return http.get(raw_url).text


def save_fetch_result(output_path, url, data):
    raw_path = gh_url_to_filepath(url)
    p = output_path / Path(raw_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data)


def create_http_session():
    # Based on https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["GET"]
    )
    http = requests.Session()
    http.mount("https://", HTTPAdapter(max_retries=retry_strategy))
    http.mount("http://", HTTPAdapter(max_retries=retry_strategy))
    return http


def main():
    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="input", help="CSV input file", required=True)
    parser.add_argument("-o", dest="output", help="Results output directory (default: 'out')", default="out")
    parser.add_argument(
        "-t", dest="threads", help="Number of download threads (default: 100)", default=100, type=int)
    args = parser.parse_args()
    # Create requests session
    http = create_http_session()
    # Process CSV file
    # Based on https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        chunks = pd.read_csv(args.input, usecols=[
                             "File external URL"], low_memory=True)
        future_to_url = {executor.submit(
            fetch_url, http, url): url for url in chunks["File external URL"]}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as e:
                print("Fetching %r generated an exception: %s" % (url, e))
                continue
            try:
                save_fetch_result(args.output, url, data)
            except Exception as e:
                print("Writing %r generated an exception: %s" % (url, e))


if __name__ == "__main__":
    main()
