#!/bin/sh

# This script reload the config for ejabberd to ensure it uses
# the latest certificates.

set -e

systemctl reload ejabberd
