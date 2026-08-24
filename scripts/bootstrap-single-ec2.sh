#!/usr/bin/env bash
set -Eeuo pipefail

if [ "${EUID}" -ne 0 ]; then
    printf 'Run this bootstrap with sudo: sudo %s\n' "$0" >&2
    exit 1
fi

log() {
    printf '[host-bootstrap] %s\n' "$*"
}

install_aws_cli() {
    if command -v aws >/dev/null 2>&1; then
        return 0
    fi
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update
        DEBIAN_FRONTEND=noninteractive apt-get install -y awscli
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y awscli || dnf install -y awscli2
    elif command -v yum >/dev/null 2>&1; then
        yum install -y awscli || yum install -y awscli2
    else
        printf 'AWS CLI is required but could not be installed on this host.\n' >&2
        exit 1
    fi
}

install_docker_debian() {
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl docker.io awscli
}

install_docker_rhel() {
    local package_manager="$1"
    "${package_manager}" install -y docker curl
}

if ! command -v docker >/dev/null 2>&1; then
    log "Installing Docker for the detected Linux distribution."
    if command -v apt-get >/dev/null 2>&1; then
        install_docker_debian
    elif command -v dnf >/dev/null 2>&1; then
        install_docker_rhel dnf
    elif command -v yum >/dev/null 2>&1; then
        install_docker_rhel yum
    else
        printf 'Unsupported host: install Docker Engine manually, then rerun this script.\n' >&2
        exit 1
    fi
fi

if ! command -v curl >/dev/null 2>&1; then
    if command -v dnf >/dev/null 2>&1; then
        dnf install -y curl
    elif command -v yum >/dev/null 2>&1; then
        yum install -y curl
    fi
fi

install_aws_cli

systemctl enable --now docker

install -d -m 0750 /etc/studytracker
docker network inspect scaler-network >/dev/null 2>&1 || docker network create scaler-network >/dev/null
docker volume inspect scaler_postgres_data >/dev/null 2>&1 || docker volume create scaler_postgres_data >/dev/null

ENV_PARAMETER_NAME="${STUDYTRACKER_ENV_PARAMETER:-}"
if [ ! -f /etc/studytracker/api.env ] && [ -n "${ENV_PARAMETER_NAME}" ]; then
    install_aws_cli
    log "Loading the application environment from encrypted Parameter Store."
    aws ssm get-parameter \
        --name "${ENV_PARAMETER_NAME}" \
        --with-decryption \
        --query 'Parameter.Value' \
        --output text > /etc/studytracker/api.env
    chmod 600 /etc/studytracker/api.env
fi

REGISTRY_TOKEN_PARAMETER="${STUDYTRACKER_REGISTRY_TOKEN_PARAMETER:-}"
if [ ! -f /etc/studytracker/ghcr-token ] && [ -n "${REGISTRY_TOKEN_PARAMETER}" ]; then
    install_aws_cli
    log "Loading the read-only registry token from encrypted Parameter Store."
    aws ssm get-parameter \
        --name "${REGISTRY_TOKEN_PARAMETER}" \
        --with-decryption \
        --query 'Parameter.Value' \
        --output text > /etc/studytracker/ghcr-token
    chmod 600 /etc/studytracker/ghcr-token
fi

login_user="${SUDO_USER:-}"
if [ -n "${login_user}" ] && id "${login_user}" >/dev/null 2>&1; then
    usermod -aG docker "${login_user}"
fi

log "Docker, scaler-network, and scaler_postgres_data are ready."
if [ -f /etc/studytracker/api.env ]; then
    log "The protected application environment is installed."
else
    log "Install /etc/studytracker/api.env or set STUDYTRACKER_ENV_PARAMETER, then run the deployment through GitHub Actions or SSM."
fi
