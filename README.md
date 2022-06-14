Scripts for the purposes of scraping Sourcegraph search results. Script `json-to-raw-url.sh` extracts raw GitHub file URLs from [src-cli](https://github.com/sourcegraph/src-cli/), and `src/github_downloader.py` downloads all the files from GitHub.

## Example Usage

```sh
src search -stream -json '${{github.event.comment.body}} file:.github/workflows COUNT:100000' | ./json-to-raw-url.sh | python3 src/github_downloader.py
```

## Why is this so useful?

This allows security researchers to run static analysis tools on a mass of GitHub repos which are fetched from Sourcegraph. Here's an example of running semgrep:

```sh
semgrep --config "p/github-actions" out
```

The output will include full repository file paths, allowing us to easily identify the vulnerable repositories.

