# tournaments-backend

## Develop

### Image building

Build the development container with this command

```bash
docker image build --target=dev --tag=tournaments-mgmt-backend:dev .
```

### Odoo start

```bash
python3 \
    odoo/odoo-bin \
        --config=/data/odoorc.conf \
        --workers=0 \
        --http-port=8069 \
        --limit-time-cpu=9999999 \
        --limit-time-real=9999999 \
        --log-handler=odoo.addons.tournaments:DEBUG \
        --log-handler=odoo.addons.maxmind_geoip2:DEBUG \
        --addons-path=odoo/odoo/addons,odoo/addons,addons \
        --data-dir=/data \
        --db_host=172.17.0.1 \
        --db_port=5432 \
        --db_user=tournaments \
        --db_password=tournaments
```

### Container start arguments fopr PyCharm

```
-v /home/user/data/tournaments:/data \
-v /opt/geolite2:/opt/geolite2:ro \
-p 0.0.0.0:8069:8069 \
-p 0.0.0.0:8072:8072 \
--rm
```
