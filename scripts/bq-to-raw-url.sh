#!/bin/bash

jq -r '"https://raw.githubusercontent.com/\(.repo_name)/HEAD/\(.path)"'
