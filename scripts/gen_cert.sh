#! /bin/sh
openssl req -newkey rsa:4096 \
            -x509 \
            -sha512 \
            -days 9999 \
            -nodes \
            -out crt \
            -keyout key \
            -subj "/C=US/ST=California/L=LA/O=CyberCert/OU=IT Department/CN=localhost" \
|| echo "Please install the openssl package"