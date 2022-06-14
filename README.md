A tool for the purposes of scraping Sourcegraph search results. Script `json-to-raw-url.sh` extracts raw GitHub file URLs from [src-cli](https://github.com/sourcegraph/src-cli/), and `src/sourcegraph_fetcher.py` downloads all the fetched files.

## Example Usage

```sh
src search -stream -json '${{github.event.comment.body}} file:.github/workflows COUNT:100000' | ./json-to-raw-url.sh | python3 src/sourcegraph_fetcher.py
```

## Why is this so useful?

This allows security researchers to run static analysis tools on a mass of GitHub repos which are fetched from Sourcegraph. Here's an example of running semgrep:

```sh
semgrep --config "p/github-actions" out
```

The output will include full repository file paths, allowing us to easily identify the vulnerable repositories.

