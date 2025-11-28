#!/usr/bin/env bash
set -euo pipefail

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew not found. Install from https://brew.sh/" >&2
  exit 1
fi

brew update
brew install open-babel --cask || brew install open-babel || true
brew install autodock-vina || true
brew install openjdk wget unzip

# Ensure Java available
/usr/libexec/java_home >/dev/null 2>&1 || true

echo "Java version:"
java -version || true

echo "OpenBabel:"
obabel -V || true

echo "Vina:"
vina --version || true

echo "System dependencies installed. Add openjdk to PATH if needed:"
echo '  export PATH="$(/usr/libexec/java_home)/bin:$PATH"'
echo "Done."
