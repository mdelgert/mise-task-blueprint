#!/usr/bin/env bash
set -euo pipefail

# Add additional desired packages in each distro mapping below.
# Package names differ across Linux distributions.

if command -v pacman >/dev/null 2>&1; then
  # Arch / Omarchy
  packages=(
    ansible
    nano
    remmina
    age
    sops
    curl
    jq
    git
    openssh
    docker
    docker-compose
  )
  echo "Detected pacman."
  printf 'Installing: %s\n' "${packages[*]}"
  sudo pacman -S --needed "${packages[@]}"

elif command -v apt-get >/dev/null 2>&1; then
  # Debian / Ubuntu
  packages=(
    ansible
    nano
    remmina
    age
    curl
    jq
    git
    openssh-client
    docker.io
  )
  echo "Detected apt."
  sudo apt-get update
  sudo apt-get install -y "${packages[@]}"

  # Compose package naming varies by Ubuntu/Debian release.
  if apt-cache show docker-compose-v2 >/dev/null 2>&1; then
    sudo apt-get install -y docker-compose-v2
  elif apt-cache show docker-compose-plugin >/dev/null 2>&1; then
    sudo apt-get install -y docker-compose-plugin
  else
    echo "NOTE: Docker Compose v2 package not found in configured apt repositories."
  fi

  # SOPS also varies by distro/repository.
  if apt-cache show sops >/dev/null 2>&1; then
    sudo apt-get install -y sops
  else
    echo "NOTE: 'sops' not found in configured apt repositories."
    echo "      Mise can manage the CLI instead: mise use -g sops"
  fi

elif command -v dnf >/dev/null 2>&1; then
  # Fedora / RHEL-family; exact availability depends on enabled repositories.
  packages=(
    ansible-core
    nano
    remmina
    age
    sops
    curl
    jq
    git
    openssh-clients
    docker
    docker-compose-plugin
  )
  echo "Detected dnf."
  printf 'Installing: %s\n' "${packages[*]}"
  sudo dnf install -y "${packages[@]}"

else
  echo "Unsupported package manager." >&2
  echo "Add a new package-manager branch to scripts/bash/install-packages.sh." >&2
  exit 1
fi

cat <<'EOF'

Baseline installation finished.

Useful checks:
  ansible --version
  nano --version
  remmina --version
  age --version
  sops --version
  docker --version

PLACEHOLDER FOR MORE PACKAGES:
  Extend the distro-specific arrays in scripts/bash/install-packages.sh.
EOF
