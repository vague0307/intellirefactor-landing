#!/usr/bin/env bash
# intellirefactor.com HTTPS 自助保障（幂等，systemd timer 每日调用）
# DNS 未解析到本机 → 静默退出等待；解析生效且证书缺失/临期 → 签发并挂 443
set -euo pipefail

DOMAIN="intellirefactor.com"
WEBROOT="/www/wwwroot/intellirefactor.com"
VHOST="/www/server/panel/vhost/nginx/intellirefactor.conf"
CERT="/etc/nginx/ssl/intellirefactor.com.pem"
KEY="/etc/nginx/ssl/intellirefactor.com.key"
SELF_IP="$(curl -s --max-time 5 http://100.100.100.200/latest/meta-data/eipv4 || true)"
[ -z "$SELF_IP" ] && SELF_IP="$(curl -s --max-time 5 ifconfig.me || true)"

log() { echo "[ensure-cert] $*"; }

# 1. DNS 是否已指向本机（未指向说明解析还没配，静默等待）
RESOLVED="$(getent hosts "$DOMAIN" | awk '{print $1}' | head -1 || true)"
if [ -z "$RESOLVED" ]; then
  log "$DOMAIN 未解析（DNS 未配置），跳过。"
  exit 0
fi
if [ -n "$SELF_IP" ] && [ "$RESOLVED" != "$SELF_IP" ]; then
  log "$DOMAIN 解析到 $RESOLVED（本机 $SELF_IP），跳过。"
  exit 0
fi
log "DNS 已生效：$DOMAIN -> $RESOLVED"

# 2. 证书仍有效（>30 天）且 443 已挂 → 无事可做
if [ -f "$CERT" ] && [ -f "$KEY" ] && openssl x509 -checkend $((30*86400)) -noout -in "$CERT" >/dev/null 2>&1; then
  log "证书仍有效（>30 天）。"
  exit 0
fi

# 3. 签发（webroot 模式走现有 80 站点的 acme-challenge location）
ACME="$HOME/.acme.sh/acme.sh"
[ -x "$ACME" ] || { log "acme.sh 未安装"; exit 1; }
log "开始签发证书…"
"$ACME" --issue --server letsencrypt -d "$DOMAIN" -d "www.$DOMAIN" \
  --webroot "$WEBROOT" --keylength ec-256 \
  --accountemail vague0307@gmail.com --force 2>&1 | tail -3

# 4. 安装证书 + 重写 vhost（80 重定向 + 443 正式块）
mkdir -p /etc/nginx/ssl
"$ACME" --install-cert -d "$DOMAIN" --ecc \
  --fullchain-file "$CERT" --key-file "$KEY" \
  --reloadcmd "nginx -s reload" 2>&1 | tail -2

cat > "$VHOST" << NGINX
# intellirefactor.com 域名出售静态站（refactor-landing 仓库部署）
# HTTPS 由 /opt/intellirefactor-landing/scripts/ensure-cert.sh 自动保障
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location ^~ /.well-known/acme-challenge/ {
        default_type "text/plain";
        root $WEBROOT;
    }
    location / {
        return 301 https://\$host\$request_uri;
    }
    access_log  /www/wwwlogs/intellirefactor.com.log;
    error_log   /www/wwwlogs/intellirefactor.com.error.log;
}
server {
    listen 443 ssl;
    http2 on;
    server_name $DOMAIN www.$DOMAIN;
    ssl_certificate     $CERT;
    ssl_certificate_key $KEY;
    ssl_session_timeout 5m;
    ssl_session_cache shared:SSL:10m;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4;
    ssl_prefer_server_ciphers on;
    root $WEBROOT;
    index index.html;

    gzip on;
    gzip_types text/css application/javascript application/json image/svg+xml;
    gzip_min_length 256;

    location /assets/ {
        add_header Cache-Control "public, max-age=2592000";
        try_files \$uri =404;
    }
    location = /index.html {
        add_header Cache-Control "no-cache";
    }
    location / {
        try_files \$uri \$uri/ =404;
    }
    access_log  /www/wwwlogs/intellirefactor.com.log;
    error_log   /www/wwwlogs/intellirefactor.com.error.log;
}
NGINX
nginx -t && nginx -s reload
log "证书已安装，443 已启用。"
