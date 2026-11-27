"""`moriarty status`: compose service health, then RabbitMQ and Postgres reachability."""

import asyncio
import json
from pathlib import Path

import aio_pika
import psycopg

from moriarty_cli.checks import Check
from moriarty_cli.envfile import resolve

CONNECT_TIMEOUT_SECONDS = 3


def parse_ps(output: str) -> list[dict[str, str]]:
    """`docker compose ps --format json`: one JSON object per line, or one array (older compose)."""
    text = output.strip()
    if not text:
        return []
    if text.startswith("["):
        rows: list[dict[str, str]] = json.loads(text)
        return rows
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def service_check(row: dict[str, str]) -> Check:
    """Running, and healthy when the service has a healthcheck."""
    state = row.get("State", "")
    health = row.get("Health", "")
    ok = state == "running" and health in ("", "healthy")
    detail = state if not health else f"{state}, {health}"
    return Check(row.get("Service", "?"), ok, detail)


def amqp_check(url: str | None) -> Check:
    if not url:
        return Check("rabbitmq (amqp)", False, "AMQP_URL is not set", "set it in infra/.env")
    try:
        asyncio.run(_amqp_connect(url))
    except Exception as exc:  # any failure to connect is the answer
        return Check("rabbitmq (amqp)", False, f"cannot connect: {type(exc).__name__}")
    return Check("rabbitmq (amqp)", True, "connected")


async def _amqp_connect(url: str) -> None:
    connection = await aio_pika.connect(url, timeout=CONNECT_TIMEOUT_SECONDS)
    await connection.close()


def postgres_check(url: str | None) -> Check:
    if not url:
        return Check("postgres (sql)", False, "DATABASE_URL is not set", "set it in infra/.env")
    try:
        with psycopg.connect(url, connect_timeout=CONNECT_TIMEOUT_SECONDS) as conn:
            conn.execute("SELECT 1")
    except psycopg.Error as exc:
        return Check("postgres (sql)", False, postgres_reason(exc))
    return Check("postgres (sql)", True, "connected")


def postgres_reason(exc: psycopg.Error) -> str:
    """The server's reason, e.g. `password authentication failed for user "moriarty"`.
    libpq never echoes the password, so the message is safe to print."""
    lines = str(exc).strip().splitlines()
    last = lines[-1] if lines else type(exc).__name__
    return last.rpartition("FATAL:")[2].strip() or type(exc).__name__


def reachability_checks(env_file: Path) -> list[Check]:
    return [
        amqp_check(resolve("AMQP_URL", env_file)),
        postgres_check(resolve("DATABASE_URL", env_file)),
    ]
