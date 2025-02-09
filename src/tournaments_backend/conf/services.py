from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def generate_services(instance: FastAPI):
    yield
