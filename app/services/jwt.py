import jwt

from config import config


def generate(user_id: int) -> str:
    payload = {
        "user_id": user_id
    }

    return encode(payload)


def encode(payload: dict) -> str:
    return jwt.encode(payload=payload, key=config.JWT_KEY)


def decode(jwt_content: str = "") -> dict:
    return jwt.decode(jwt=jwt_content, key=config.JWT_KEY, algorithms=["HS256"])
