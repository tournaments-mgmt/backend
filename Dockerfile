FROM python:3.12 AS base
ENV DEBIAN_FRONTENT=noninteractive
ENV HOME=/data
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install curl ca-certificates lsb-release \
    && install -d /usr/share/postgresql-common/pgdg \
    && curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    && echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt update \
    && apt -y install \
      postgresql-client \
      libpq5 \
    && rm -R /var/lib/apt/*
RUN groupadd -g 1000 user \
    && useradd --home-dir=/data --gid=1000 --no-create-home --shell=/bin/bash --uid=1000 user \
    && mkdir /data \
    && chown 1000:1000 /data

FROM base AS venv
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install build-essential automake autoconf libtool pkg-config cmake \
      libpq-dev \
    && rm -R /var/lib/apt/*
RUN python3 -m venv /venv \
    && . /venv/bin/activate \
    && python3 -m pip install --upgrade pip setuptools wheel poetry
RUN mkdir /project
COPY pyproject.toml /project/pyproject.toml
COPY poetry.lock /project/poetry.lock
RUN cd /project \
    && . /venv/bin/activate \
    && poetry install --no-root

FROM base AS odoo
COPY --from=venv /venv /venv

FROM odoo AS dev
COPY pyproject.toml /project/pyproject.toml
COPY poetry.lock /project/poetry.lock
RUN cd /project \
    && . /venv/bin/activate \
    && poetry install --no-root --with=dev
USER user

FROM odoo AS prod
COPY odoo /odoo
COPY addons /addons
COPY docker/entrypoint.sh /entrypoint.sh
VOLUME /data
RUN chown -R 1000:1000 /data
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
