#!/usr/bin/env bash
set -euo pipefail

output_file="${1:-.deploy/vertice.env}"
mkdir -p "$(dirname "$output_file")"

# O arquivo é gerado no runner a partir de Environment Variables/Secrets do
# GitHub e enviado por SSH. Nenhum segredo precisa entrar no Git.
write_key() {
  local key="$1"
  local value="${!key-}"
  value="${value//$'\r'/}"
  value="${value//$'\n'/\\n}"
  [[ -n "$value" ]] || return 0
  printf "%s='%s'\n" "$key" "$value" >> "$output_file"
}

: > "$output_file"
for key in \
  OPENAI_API_KEY OPENAI_API_BASE LLM_MODEL LLM_TEMPERATURE LLM_REQUEST_TIMEOUT \
  AUDIT_RECURSION_LIMIT COPILOT_RECURSION_LIMIT AUDIT_SNAPSHOT_PATH \
  RESEND_API_KEY RESEND_FROM_EMAIL RESEND_TO_EMAIL APP_BASE_URL AGENT_DEEP_LINK_PATH \
  AUDIT_CRON_SCHEDULE; do
  write_key "$key"
done

chmod 600 "$output_file"
