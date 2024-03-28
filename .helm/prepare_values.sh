#!/usr/bin/env bash

set -e
set +x

SECRETS_RAW=$(vault kv get -format json "kv/$1")
cat ./launchpad/values.yaml.tpl > ./launchpad/values.yaml

for k in $(jq -r '.data.data | keys | .[]' <<< $SECRETS_RAW); do
  v=$(jq -r ".data.data.$k" <<< $SECRETS_RAW)
  echo "    $k: \"$v\"" >> ./launchpad/values.yaml
done
