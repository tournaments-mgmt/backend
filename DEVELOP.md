# tournaments-backend

## Develop

### Image building

Build the development container with this command

```bash
docker image build --target=dev --tag=tournaments-mgmt-backend:dev .
```

### Environment vars

```bash
JWT_SIGN_KEY="-----BEGIN PRIVATE KEY-----\nMC4CAQAwBQYDK2VwBCIEIBgL/kfqHKHq9nkUYtfmj7lFQ+OUb+ymd4VbzYUse4Ef\n-----END PRIVATE KEY-----\n"
JWT_ENCRYPT_KEY="SXkFiTqwekNLvITKukrZ4sp3psTjpVkDyelHBOeSF2M="
```
