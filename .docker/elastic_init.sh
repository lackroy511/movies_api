#!/bin/sh
set -e

create_index_if_missing() {
  index_name=$1
  json_file=$2

  echo "Checking ${index_name} index…"
  http_code=$(curl -s -o /dev/null -w '%{http_code}' "http://movies_elastic:9200/${index_name}")

  if [ "$http_code" = "404" ]; then
    echo "Creating ${index_name} index from ${json_file}"
    curl -sS -X PUT "http://movies_elastic:9200/${index_name}" \
      -H 'Content-Type: application/json' \
      --data-binary @"${json_file}"
  else
    echo "${index_name} index already exists (HTTP $http_code)"
  fi
}

# Create the three indices
create_index_if_missing movies /movies-index.json
create_index_if_missing genres /genres-index.json
create_index_if_missing persons /persons-index.json

echo "All done."