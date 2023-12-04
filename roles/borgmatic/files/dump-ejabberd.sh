#!/bin/sh

# Helper script for borgmatic to dump ejabberd databases.

set -e

mkdir -p /tmp/borgmatic/ejabberd/

ejabberdctl --no-timeout backup /tmp/ejabberd.backup

# ejabberd uses PrivateTmp, so lets use this hack to copy the backup
# to the place where we expect it for borgmatic.
PRIVATE_TMP_BACKUP_LOCATION="$(find /tmp/systemd-private-* -type f -name ejabberd.backup)"

if [ "$PRIVATE_TMP_BACKUP_LOCATION" = "" ]; then
  echo "Couldn't find generated backup"
  exit 1
fi

if [ "$(echo "$PRIVATE_TMP_BACKUP_LOCATION" | wc -l)" -gt 1 ]; then
  echo "Something went wrong. Found more than one backup."
  exit 1
fi

mv "$PRIVATE_TMP_BACKUP_LOCATION" /tmp/borgmatic/ejabberd/ejabberd.backup
chmod 600 /tmp/borgmatic/ejabberd/ejabberd.backup
chown root:root /tmp/borgmatic/ejabberd/ejabberd.backup
