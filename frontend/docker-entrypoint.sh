#!/bin/sh
set -e

# Update nginx to listen on Cloud Run PORT (if set)
if [ -n "$PORT" ]; then
  echo "Configuring nginx to listen on port $PORT"
  sed -i "s/listen 8080;/listen $PORT;/" /etc/nginx/conf.d/default.conf
fi

# Execute the CMD
exec "$@"

