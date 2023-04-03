#! /bin/sh

OPENSSL_CMD=$(which openssl)

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
COMMAND=$1
SECRET_NAME=${2:-"wrapme-envoy-certificates"}

function random_string() {
    local length=${1:-10}

    head /dev/urandom | tr -dc a-zA-Z0-9 | head -c$length
}

function create_secret() {
    local tmp_path=$(mktemp -d --tmpdir=/tmp podman-cert-secret.XXXXXX)
    local server_key=${tmp_path}/certificate.key
    local server_csr=${tmp_path}/certificate.csr
    local server_cert=${tmp_path}/certificate.pem

    # Generate the private key
    $OPENSSL_CMD genrsa -out $server_key 4096 2>/dev/null

    local ext_file=${SCRIPT_DIR}/wrapme-csr-config.cnf
    # Generate the certificate signing request
    $OPENSSL_CMD req -new -key $server_key -out $server_csr -config $ext_file 2>/dev/null

    # Generate the certificate
    $OPENSSL_CMD x509 -req -days 3650 -in $server_csr -signkey $server_key -out $server_cert 2>/dev/null

    local cert_secret_file=${tmp_path}/secret_$(random_string)
    cat > $cert_secret_file <<EOF
kind: Secret
apiVersion: v1
metadata:
  name: $SECRET_NAME
data:
  certificate.key: $(cat $server_key | base64)
  certificate.pem: $(cat $server_cert | base64)
EOF
    podman secret create $SECRET_NAME $cert_secret_file
}

function remove_secret() {
    podman secret rm $SECRET_NAME
}

# Check if the secrets exists (change to use secret exists once released)
podman secret inspect --format {{.Spec.Name}} $SECRET_NAME > /dev/null 2>&1

case $COMMAND in
    create)
    if [[ $? -ne 0 ]]; then
        create_secret
    fi
    ;;
    remove)
    if [[ $? -eq 0 ]]; then
        remove_secret
    fi
    ;;
    *)
    echo Unsupported command $COMMAND
    ;;
esac
