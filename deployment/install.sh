#!/usr/bin/env bash
set -euo pipefail

TARGET=/opt/kohaguard
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"

echo "== KohaGuard installer =="
if [[ $EUID -ne 0 ]]; then echo "Run with sudo/root"; exit 1; fi

apt-get update
apt-get install -y python3 python3-venv python3-pip curl apache2

mkdir -p "$TARGET"
cp -a "$SOURCE/backend" "$TARGET/"
cp -a "$SOURCE/frontend" "$TARGET/"
cp -a "$SOURCE/.env.example" "$TARGET/.env.example"

if [[ ! -f "$TARGET/.env" ]]; then
  cp "$TARGET/.env.example" "$TARGET/.env"
  echo "IMPORTANT: edit $TARGET/.env before production use."
fi

python3 -m venv "$TARGET/venv"
"$TARGET/venv/bin/pip" install --upgrade pip
"$TARGET/venv/bin/pip" install -r "$TARGET/backend/requirements.txt"

mkdir -p "$TARGET/frontend/static/vendor" "$TARGET/data"
curl -fL "https://cdn.jsdelivr.net/npm/@zxing/browser@0.2.1/umd/zxing-browser.min.js" \
  -o "$TARGET/frontend/static/vendor/zxing-browser.min.js"

cp "$SOURCE/deployment/kohaguard.service" /etc/systemd/system/kohaguard.service
chown -R www-data:www-data "$TARGET"
chmod 750 "$TARGET"
chmod 640 "$TARGET/.env" || true

systemctl daemon-reload
systemctl enable kohaguard

echo
cat <<EOF
Installation files are prepared.

1. Edit: $TARGET/.env
2. Test DB credentials.
3. Start: systemctl restart kohaguard
4. Check: curl http://127.0.0.1:8096/api/status
5. Configure Apache using deployment/apache-kohaguard.conf

Do not expose port 8096 publicly in a production deployment.
EOF
