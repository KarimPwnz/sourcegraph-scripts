jq -r '. | select(.repository != null) | "\(.repository)/HEAD/\(.path)"' |
cut -d '/' -f 2- |
awk '{print "https://raw.githubusercontent.com/"$1}'
