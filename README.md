Scripts for the purposes of scraping Sourcegraph search results. Script `scripts/json-to-raw-url.sh` extracts raw GitHub file URLs from [src-cli](https://github.com/sourcegraph/src-cli/), and `scripts/github_downloader.py` downloads all the files from GitHub.

## Example Usage

```sh
$ src search -stream -json '${{github.event.comment.body}} file:.github/workflows COUNT:100000' | ./scripts/json-to-raw-url.sh | python3 scripts/github_downloader.py
```

## Why is this so useful?

This allows security researchers to run static analysis tools on a mass of GitHub repos which are fetched from Sourcegraph. Here's an example of running [Semgrep](https://semgrep.dev):

```sh
$ semgrep --config "p/github-actions" out
```

The output will include full repository file paths, allowing us to easily identify the vulnerable repositories.

## How to install

```sh
$ git clone https://github.com/KarimPwnz/sourcegraph-scripts.git
$ cd sourcegraph-scripts
$ pip install -r requirements.txt
```

