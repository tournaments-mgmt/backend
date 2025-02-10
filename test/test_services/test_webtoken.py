async def test_encrypt_decrypt(webtoken_service):
    data: dict = {"param": "value"}

    token: str = await webtoken_service.encrypt(data)
    data_dec: dict = await webtoken_service.decrypt(token)

    assert data_dec == data
