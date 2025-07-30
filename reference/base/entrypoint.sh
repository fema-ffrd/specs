#!/bin/bash
set -e

CONFIG_JSON="$1"

# Just call validate, which handles both validation and downloading now
validate "$CONFIG_JSON"

