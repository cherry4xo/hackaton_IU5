# conftest.py
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Путь к корню проекта
root = Path(__file__).parent

# Добавляем все services/*/ в sys.path
services_dir = root / "services"
if services_dir.exists():
    for service in services_dir.iterdir():
        if service.is_dir():
            sys.path.insert(0, str(service))


@pytest.fixture(autouse=True)
def mock_minio_client():
    """Мокаем MinIOClient и все его методы."""
    with patch("services.calculation.app.utils.minio_client.MinIOClient") as mock:
        client = Mock()
        client.bucket_exists.return_value = True
        client.make_bucket.return_value = None
        client.fput_object.return_value = None
        client.get_object.return_value.read.return_value = b"fake fits data"
        mock.return_value = client
        yield client


@pytest.fixture(autouse=True)
def mock_get_minio_client():
    """Мокаем фабрику get_minio_client."""
    with patch("services.calculation.app.utils.minio_client.get_minio_client") as mock:
        mock.return_value = Mock()
        yield mock.return_value