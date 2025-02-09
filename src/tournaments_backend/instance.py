from fastapi import FastAPI

from tournaments_backend import conf

app: FastAPI = conf.fastapi.create_instance()
