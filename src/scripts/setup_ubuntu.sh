#!/usr/bin/env bash
set -euo pipefail

sudo apt-get -qq update
sudo apt-get -qq install -y default-jre openbabel unzip wget python3-tk || true
sudo apt-get -qq install -y autodock-vina fpocket || true

echo "Java version:"
java -version || true

echo "OpenBabel:"
obabel -V || true

echo "Vina:"
vina --version || true

echo "Done."
