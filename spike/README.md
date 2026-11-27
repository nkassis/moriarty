# Spike

One agent resolves one coolant fault over RabbitMQ and MCP. Run everything from `spike/`.

## Setup

```sh
cp .env.example .env   # then fill in every value
```

## Run

```sh
docker compose up -d --build
```

Start the viewer within about 30 seconds. The fault fires at 30 seconds and the run is over about a minute later.

```sh
uv run --env-file .env python -m spike.tail
```

## Stop

```sh
docker compose down
```

## Test

```sh
uv run pytest
```
