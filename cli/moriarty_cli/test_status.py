import json

import psycopg

from moriarty_cli.status import (
    amqp_check,
    parse_ps,
    postgres_check,
    postgres_reason,
    service_check,
)

ROWS = [
    {"Service": "rabbitmq", "State": "running", "Health": "healthy"},
    {"Service": "jaeger", "State": "running", "Health": ""},
]


def test_parse_ps_reads_one_object_per_line() -> None:
    assert parse_ps("\n".join(json.dumps(row) for row in ROWS)) == ROWS


def test_parse_ps_reads_an_array_and_empty_output() -> None:
    assert parse_ps(json.dumps(ROWS)) == ROWS
    assert parse_ps("  \n") == []


def test_service_is_ok_when_running_and_healthy_or_without_a_healthcheck() -> None:
    assert service_check(ROWS[0]).ok
    assert service_check(ROWS[1]).ok
    assert not service_check({"Service": "pg", "State": "running", "Health": "starting"}).ok
    assert not service_check({"Service": "pg", "State": "exited", "Health": ""}).ok


def test_reachability_fails_without_urls() -> None:
    assert not amqp_check(None).ok
    assert not postgres_check(None).ok


def test_reachability_fails_on_a_closed_port() -> None:
    assert not amqp_check("amqp://u:p@127.0.0.1:1/").ok
    assert not postgres_check("postgresql://u:p@127.0.0.1:1/db").ok


def test_postgres_reason_is_the_server_message_without_the_prefix() -> None:
    exc = psycopg.OperationalError(
        'connection failed: connection to server at "127.0.0.1", port 5432 failed: '
        'FATAL:  password authentication failed for user "moriarty"'
    )
    assert postgres_reason(exc) == 'password authentication failed for user "moriarty"'
    assert postgres_reason(psycopg.OperationalError("")) == "OperationalError"
