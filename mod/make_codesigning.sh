#!/bin/bash
# Creates throwaway "fake" codesigning material for the build, the same way
# Swiftgram's own build-system/fake-codesigning works: a self-signed certificate
# and a provisioning profile signed with it. The resulting .ipa is NOT installable
# as is; Sideloadly re-signs it with the user's free Apple ID.
#
# Usage: mod/make_codesigning.sh <output-dir> <team-id> <bundle-id>
set -euo pipefail

OUT="$1"
TEAM_ID="$2"
BUNDLE_ID="$3"
# macOS' own LibreSSL writes .p12 files that `security import` accepts.
OPENSSL=/usr/bin/openssl

rm -rf "$OUT"
mkdir -p "$OUT/certs" "$OUT/profiles"
WORK="$(mktemp -d)"

cat > "$WORK/cert.cnf" <<EOF
[req]
distinguished_name = dn
prompt = no
x509_extensions = ext
[dn]
CN = Apple Development: Lumigram ($TEAM_ID)
OU = $TEAM_ID
O = Lumigram
C = US
[ext]
keyUsage = critical, digitalSignature
extendedKeyUsage = critical, codeSigning
basicConstraints = critical, CA:false
EOF

"$OPENSSL" req -x509 -newkey rsa:2048 -nodes -days 3650 \
    -keyout "$WORK/key.pem" -out "$WORK/cert.pem" -config "$WORK/cert.cnf"
"$OPENSSL" x509 -in "$WORK/cert.pem" -outform der -out "$OUT/certs/Public.cer"
"$OPENSSL" pkcs12 -export -inkey "$WORK/key.pem" -in "$WORK/cert.pem" \
    -out "$OUT/certs/SelfSigned.p12" -passout pass:

CERT_B64="$(base64 < "$OUT/certs/Public.cer" | tr -d '\n')"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EXPIRES="$(date -u -v+1y +%Y-%m-%dT%H:%M:%SZ)"
UUID="$(uuidgen)"

cat > "$WORK/profile.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>AppIDName</key>
    <string>Lumigram</string>
    <key>ApplicationIdentifierPrefix</key>
    <array><string>$TEAM_ID</string></array>
    <key>CreationDate</key>
    <date>$NOW</date>
    <key>Platform</key>
    <array><string>iOS</string></array>
    <key>DeveloperCertificates</key>
    <array><data>$CERT_B64</data></array>
    <key>Entitlements</key>
    <dict>
        <key>application-identifier</key>
        <string>$TEAM_ID.$BUNDLE_ID</string>
        <key>aps-environment</key>
        <string>development</string>
        <key>com.apple.developer.team-identifier</key>
        <string>$TEAM_ID</string>
        <key>com.apple.security.application-groups</key>
        <array><string>group.$BUNDLE_ID</string></array>
        <key>get-task-allow</key>
        <true/>
        <key>keychain-access-groups</key>
        <array><string>$TEAM_ID.*</string></array>
    </dict>
    <key>ExpirationDate</key>
    <date>$EXPIRES</date>
    <key>Name</key>
    <string>Lumigram Fake Development</string>
    <key>ProvisionsAllDevices</key>
    <true/>
    <key>TeamIdentifier</key>
    <array><string>$TEAM_ID</string></array>
    <key>TeamName</key>
    <string>Lumigram</string>
    <key>TimeToLive</key>
    <integer>365</integer>
    <key>UUID</key>
    <string>$UUID</string>
    <key>Version</key>
    <integer>1</integer>
</dict>
</plist>
EOF

"$OPENSSL" smime -sign -binary -nodetach -outform der \
    -signer "$WORK/cert.pem" -inkey "$WORK/key.pem" \
    -in "$WORK/profile.plist" -out "$OUT/profiles/Telegram.mobileprovision"

rm -rf "$WORK"
security cms -D -i "$OUT/profiles/Telegram.mobileprovision" > /dev/null
echo "make_codesigning: created fake codesigning for $TEAM_ID.$BUNDLE_ID in $OUT"
