#!/usr/bin/env bash

export MAPBOX_TOKEN="pk.eyJ1IjoiMjk5Mjk5IiwiYSI6ImNsZ3V2Ymo4cTBrN2IzY2tsZzUzbGMybmwifQ.UmEHxJGkmirEPC4Oc-TZjg"
export SKIP_FW_QUERY="1"
export FINGERPRINT="TOYOTA_COROLLA_TSS2"
export PASSIVE="0"
export NOBOARD="1"

exec ./launch_chffrplus.sh
