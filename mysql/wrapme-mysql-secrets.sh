#!/bin/sh
COMMAND=$1

SECRETS_BASE_NAME=${2:-"wrapme-mysql-root-password"}
RAW_SECRET_NAME=$SECRETS_BASE_NAME-container
KUBE_SECRET_NAME=$SECRETS_BASE_NAME-kube

function random_string() {
    local length=${1:-10}

    head /dev/urandom | tr -dc a-zA-Z0-9 | head -c$length
}

function create_secrets() {
    local password=$(random_string)

    local tmp_path=$(mktemp -d --tmpdir=/tmp podman-raw-secret.XXXXXX)
    local raw_secret_file=${tmp_path}/secret_$(random_string)
    local kube_secret_file=${tmp_path}/secret_$(random_string)


    echo -n $password > $raw_secret_file
    podman secret create $RAW_SECRET_NAME $raw_secret_file

    cat > $kube_secret_file <<EOF
kind: Secret
apiVersion: v1
metadata:
  name: $KUBE_SECRET_NAME
data:
  password: $(echo -n $password | base64 )
EOF
    podman secret create $KUBE_SECRET_NAME $kube_secret_file
}

function remove_secrets() {
    podman secret rm $RAW_SECRET_NAME
    podman secret rm $KUBE_SECRET_NAME
}

# Check if the secrets already exists (change to use secret exists once released)
podman secret inspect --format {{.Spec.Name}} $RAW_SECRET_NAME > /dev/null 2>&1

case $COMMAND in
    create)
    if [[ $? -ne 0 ]]; then
        create_secrets
    fi
    ;;
    remove)
    if [[ $? -eq 0 ]]; then
        remove_secrets
    fi
    ;;
    *)
    echo Unsupported command $COMMAND
    ;;
esac
