#!/bin/bash

set -a

USER="user"

if [ -z "${HTTP_PORT}" ]; then
  HTTP_PORT="8069"
fi

if [ -z "${GEVENT_PORT}" ]; then
  GEVENT_PORT="8072"
fi

if [ -z "${WORKERS}" ]; then
  WORKERS="2"
fi

if [ -z "${DB_HOST}" ]; then
  DB_HOST="postgres"
fi

if [ -z "${DB_PORT}" ]; then
  DB_PORT="5432"
fi

if [ -z "${DB_USERNAME}" ]; then
  DB_USERNAME="odoo"
fi

if [ -z "${DB_PASSWORD}" ]; then
  DB_PASSWORD="odoo"
fi

if [ -z "${DB_NAME}" ]; then
  ODOO_CMD_DATABASE=""
else
  ODOO_CMD_DATABASE="--database=${DB_NAME}"
fi

if [ -z "${DATADIR}" ]; then
  DATADIR="/data"
fi

if [ -z "${ADDONS_PATH}" ]; then
  ADDONS_PATH="/odoo/odoo/addons,/odoo/addons,/addons"
fi

readarray -t INIT_ADDONS < <(find addons -mindepth 1 -maxdepth 1 -type d ! -empty -exec basename '{}' ';')

if [ -z "${ADDONS_LIST}" ]; then
  ADDONS_LIST="$(printf ",%s" "${INIT_ADDONS[@]}" | sed -e "s/^,//g")"
fi

if [ -z "${ADDONS_LOAD}" ]; then
  ADDONS_LOAD="web"
fi

if [ -z "${TEST_FLAGS}" ]; then
  TEST_FLAGS="--test-enable --log-level=test --test-tags=$(printf ",/%s" "${INIT_ADDONS[@]}" | sed -e "s/^,//g")"
fi

if [ -z "${MODE}" ]; then
  MODE="odoo"
fi

CONFIG="${DATADIR}/odoorc.conf"

chown user:user "${DATADIR}"

function run_odoo() {
  cd /odoo || exit 1

  ODOO_CMD_RUN=""

  if [ "${1}" = "test" ]; then
    ODOO_CMD_RUN="--limit-time-cpu=9999999 --limit-time-real=9999999 --stop-after-init ${TEST_FLAGS}"
    WORKERS="0"
  elif [ "${1}" = "db" ]; then
    ODOO_CMD_RUN="--stop-after-init --update=all"
    WORKERS="0"
  fi

  touch "${CONFIG}"

  set -x

  /venv/bin/python3 \
    /odoo/odoo-bin \
    --config="${CONFIG}" \
    --addons-path="${ADDONS_PATH}" \
    --http-port="${HTTP_PORT}" \
    --gevent-port="${GEVENT_PORT}" \
    --data-dir="${DATADIR}" \
    --workers="${WORKERS}" \
    --db_host="${DB_HOST}" \
    --db_port="${DB_PORT}" \
    --db_user="${DB_USERNAME}" \
    --db_password="${DB_PASSWORD}" \
    ${ODOO_CMD_DATABASE} \
    --proxy-mode \
    --load="${ADDONS_LOAD}" \
    --without-demo="all" \
    --init="${ADDONS_LIST}" \
    ${ODOO_CMD_RUN}
}

function run_api() {
  export PYTHONPATH="/app:/odoo"

  if [ "${1}" = "test" ]; then
    cd /app_tests || exit 1
    /venv/bin/pytest
    return
  fi

  cd /app || exit 1

  touch "${CONFIG}"

  /venv/bin/python3 main.py
}

function run_update_probe() {
  cd /update_probe || exit 1
  /venv/bin/python3 main.py
}

export -f run_odoo
export -f run_api
export -f run_update_probe

RUN_CMD=""

case "${MODE}" in
  db)
    RUN_CMD="run_odoo db"
    ;;
  odoo)
    RUN_CMD="run_odoo"
    ;;
  odoo-test)
    RUN_CMD="run_odoo test"
    ;;
  api)
    RUN_CMD="run_api"
    ;;
  api-test)
    RUN_CMD="run_api test"
    ;;
  update_probe)
    RUN_CMD="run_update_probe"
    ;;
  *)
    echo "Invalid mode"
    exit 1
    ;;
esac


su \
  --preserve-environment \
  --shell /bin/bash \
  --command \
  "${RUN_CMD}" \
  "${USER}"

exit ${?}
