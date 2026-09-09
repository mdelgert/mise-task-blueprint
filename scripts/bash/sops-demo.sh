#!/usr/bin/env bash
set -euo pipefail

demo_dir="${MISE_ORIGINAL_CWD:-$PWD}/.mise-sops-demo"
identity="${demo_dir}/age-identity.txt"
plain="${demo_dir}/secrets.yaml"
encrypted="${demo_dir}/secrets.enc.yaml"
decrypted="${demo_dir}/secrets.decrypted.yaml"

mkdir -p "$demo_dir"
chmod 700 "$demo_dir"
umask 077

if [[ ! -f "$identity" ]]; then
  age-keygen -o "$identity" >/dev/null
fi

recipient="$(age-keygen -y "$identity")"

cat > "$plain" <<'EOF'
demo:
  username: example-user
  api_token: not-a-real-secret
EOF

SOPS_AGE_RECIPIENTS="$recipient" sops encrypt \
  --input-type yaml \
  --output-type yaml \
  "$plain" > "$encrypted"

SOPS_AGE_KEY_FILE="$identity" sops decrypt \
  --input-type yaml \
  --output-type yaml \
  "$encrypted" > "$decrypted"

rm -f "$plain"

cat <<EOF
Created SOPS demo:
  identity:  $identity
  encrypted: $encrypted
  decrypted: $decrypted

The plaintext source was deleted.
The demo data is intentionally fake.
Do not commit the identity file.
EOF
