FROM python:3.10-bookworm AS base
ENV DEBIAN_FRONTENT=noninteractive
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install \
      vim \
      curl \
      gnupg \
      patch \
      coreutils \
      libpng16-16 \
      libtiff6 \
      libffi8 \
      libpq5 \
      libfontconfig1 \
      libfreetype6 \
      libgif7 \
      libjpeg62-turbo \
      zlib1g \
      liblcms2-2 \
      libwebp7 \
      libtcl8.6 \
      libimagequant0 \
      libfribidi0 \
      libharfbuzz0b \
      libopenjp2-7 \
      libssl3 \
      libevent-2.1-7 \
      libxml2  \
      libldap-2.5-0 \
      libusb-0.1-4 libusb-1.0-0 \
      libxslt1.1 \
      libsasl2-2 \
      libexpat1 \
      libreadline8 \
      libncurses6 libncursesw6 \
      libmagic1 \
      libdmtx0b \
    && rm -R /var/lib/apt/*
RUN curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/postgresql.gpg \
        && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/postgresql.list \
    && apt update \
    && apt install -y postgresql-client

FROM base AS base-dev
ENV DEBIAN_FRONTENT=noninteractive
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install \
      build-essential automake autoconf libtool pkg-config cmake swig rustc cargo \
      libpng-dev \
      libtiff-dev \
      libffi-dev \
      libpq-dev \
      libfontconfig1-dev \
      libfreetype-dev \
      libgif-dev \
      libjpeg-dev \
      zlib1g-dev \
      liblcms2-dev \
      libwebp-dev \
      tcl-dev \
      libimagequant-dev \
      libfribidi-dev \
      libharfbuzz-dev \
      libopenjp2-7-dev \
      libssl-dev \
      libevent-dev \
      libxml2-dev \
      libldap2-dev \
      libusb-dev libusb-1.0-0-dev \
      libxslt1-dev \
      libsasl2-dev \
      libexpat1-dev \
      libreadline-dev \
      libncurses-dev \
      libmagic-dev \
      libdmtx-dev

FROM base-dev AS venv
RUN mkdir /requirements
COPY odoo/requirements.txt /requirements/odoo.txt
COPY requirements.txt /requirements/project.txt
ENV MAKEFLAGS=6
RUN python3 -m venv /venv \
    && /venv/bin/pip3 install --upgrade pip setuptools wheel \
    && /venv/bin/pip3 install --requirement=/requirements/odoo.txt
RUN /venv/bin/pip3 install --requirement=/requirements/project.txt

FROM base AS odoo
RUN apt update \
    && apt -y dist-upgrade \
    && apt -y install wget \
    && wget "https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bookworm_amd64.deb" \
    && ( dpkg -i *.deb; apt -y install -f ) \
    && rm -Rf /var/lib/apt/* *.deb
COPY --from=venv /venv /venv
RUN mkdir /odoo /addons /data /app /opt/geolite2

FROM odoo AS prod
COPY odoo/odoo /odoo/odoo
COPY odoo/odoo-bin /odoo

CMD rm -rf /odoo/odoo/addons/test*

COPY odoo/addons/auth_signup /odoo/addons/auth_signup
COPY odoo/addons/auth_totp /odoo/addons/auth_totp
COPY odoo/addons/auth_totp_mail /odoo/addons/auth_totp_mail
COPY odoo/addons/base_import /odoo/addons/base_import
COPY odoo/addons/base_install_request /odoo/addons/base_install_request
COPY odoo/addons/base_setup /odoo/addons/base_setup
COPY odoo/addons/bus /odoo/addons/bus
COPY odoo/addons/contacts /odoo/addons/contacts
COPY odoo/addons/google_gmail /odoo/addons/google_gmail
COPY odoo/addons/http_routing /odoo/addons/http_routing
COPY odoo/addons/mail /odoo/addons/mail
COPY odoo/addons/mail_bot /odoo/addons/mail_bot
COPY odoo/addons/phone_validation /odoo/addons/phone_validation
COPY odoo/addons/privacy_lookup /odoo/addons/privacy_lookup
COPY odoo/addons/web /odoo/addons/web
COPY odoo/addons/web_editor /odoo/addons/web_editor
COPY odoo/addons/web_kanban_gauge /odoo/addons/web_kanban_gauge
COPY odoo/addons/web_tour /odoo/addons/web_tour

COPY web/web_responsive /odoo/addons/web_responsive
COPY web/web_refresher /odoo/addons/web_refresher
COPY web/web_theme_classic /odoo/addons/web_theme_classic
COPY web/web_tree_many2one_clickable /odoo/addons/web_tree_many2one_clickable
COPY web/web_advanced_search /odoo/addons/web_advanced_search
COPY web/web_timeline /odoo/addons/web_timeline
COPY web/web_chatter_position /odoo/addons/web_chatter_position
COPY web/web_copy_confirm /odoo/addons/web_copy_confirm
COPY web/web_group_expand /odoo/addons/web_group_expand
COPY web/web_no_bubble /odoo/addons/web_no_bubble
COPY web/web_notify /odoo/addons/web_notify

COPY addons/ /addons

COPY app/ /app
COPY app_tests/ /app_tests

COPY update_probe /update_probe

COPY docker/patches/odoo-remove_upgradable_addons.patch /patches/
RUN ( cd /odoo && patch -Np1 -i /patches/odoo-remove_upgradable_addons.patch )

VOLUME /data
VOLUME /opt/geolite2
ENV HOME /data

RUN groupadd -g 1000 user \
    && useradd --home-dir /data --gid 1000 --no-create-home --shell /bin/false --uid 1000 user \
    && chown -R 1000:1000 /data

COPY /docker/run.sh /run.sh
RUN chmod 0755 /run.sh
ENTRYPOINT ["/bin/bash", "/run.sh"]
