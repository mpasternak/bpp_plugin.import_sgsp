from pathlib import Path
from typing import Any

import pytest
from django.apps import AppConfig
from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_schema(sender: AppConfig, **kwargs: Any) -> None:
    with connection.cursor() as cursor:
        cursor.execute(open(Path(__file__).parent / "test_db_extra_schema.sql").read())


@pytest.mark.parametrize(
    "url",
    [
        "sgsp_artykul",
        "sgsp_journal",
        "sgsp_komorka",
        "sgsp_obcy_autor",
        "sgsp_pracownik",
    ],
)
def test_import_sgsp_admin(admin_client, url):
    res = admin_client.get("/admin/")
    assert res.status_code == 200

    res = admin_client.get(f"/admin/import_sgsp/{url}/")
    assert res.status_code == 200

    res = admin_client.get(f"/admin/import_sgsp/{url}/?q=123")
    assert res.status_code == 200
