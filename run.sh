#!/usr/bin/env bash
project_root=$(pwd)
gen_dotenv() {
  skey=$(python3 ./scripts/gen_secret_key.py)
  echo "What is your host?  default:(localhost:8000):"
  read host
  [[ -z "${host// /}" ]] && host='localhost:8000'
  echo "F1L3_SECRET_KEY=${skey}" > ./.env
  echo "F1L3_HOST=${host}" >> ./.env
}

[ -f './.env' ] || gen_dotenv

gen_cert() {
  cd local_cert || return
  rm crt key -rf
  sh ../scripts/gen_cert.sh
}
([ -f './local_cert/crt' ] || [ -f './local_cert/key' ]) || gen_cert

cd "${project_root}"||exit
python3 manage.py makemigrations && python3 manage.py migrate
gunicorn --certfile=./local_cert/crt --keyfile=./local_cert/key f1l3.wsgi:application -w 8