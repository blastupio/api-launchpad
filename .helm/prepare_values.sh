#!/usr/bin/env bash

set -e
set -x

PRODUCTION_SECRETS_RAW=$(vault kv get -format json "kv/production")
cat ./launchpad/values.yaml.tpl > ./launchpad/values.yaml

for k in $(jq -r '.data.data | keys | .[]' <<< $PRODUCTION_SECRETS_RAW); do
  v=$(jq -r ".data.data.$k" <<< $PRODUCTION_SECRETS_RAW)
  echo "      $k: \"$v\"" >> ./launchpad/values.yaml
done
