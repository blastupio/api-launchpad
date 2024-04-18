# API-launchpad

## Running locally

1. Install dependencies via Poetry

```{shell}
poetry shell
poetry install
```

2. Create `.env` file and fill it with proper values

```{shell}
cp .env.example .env
```

3. Run your server

```{shell}
make dev
```

4. Run neccesary services (Redis and DB)

```{shell}
make up
```
