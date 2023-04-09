#!/bin/sh

set -e

umask 0037

DOMAIN=localhost
TARGET_DIR=/etc/ejabberd

TMP_DIR=$(mktemp -d)

trap 'rm -R $TMP_DIR' EXIT INT TERM

cat <<EOF > "$TMP_DIR/config"
[dn]
CN=$DOMAIN
[req]
distinguished_name = dn
[EXT]
subjectAltName=DNS:$DOMAIN,DNS:conference.$DOMAIN,DNS:pubsub.$DOMAIN
keyUsage=digitalSignature
extendedKeyUsage=serverAuth"
EOF

openssl req -x509 -out $TMP_DIR/$DOMAIN.crt -keyout $TMP_DIR/$DOMAIN.key \
  -newkey rsa:2048 -nodes -sha256 -days 90 \
  -subj "/CN=$DOMAIN" -extensions EXT -config "$TMP_DIR/config"

cat $TMP_DIR/$DOMAIN.key > $TMP_DIR/$DOMAIN.pem
cat $TMP_DIR/$DOMAIN.crt >> $TMP_DIR/$DOMAIN.pem

chgrp ejabberd $TMP_DIR/$DOMAIN.pem

mv $TMP_DIR/$DOMAIN.pem $TARGET_DIR/$DOMAIN.pem
