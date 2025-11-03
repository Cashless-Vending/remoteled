import sys
from pathlib import Path
import types

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

sys.modules.setdefault("stripe", types.SimpleNamespace())

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.api.auth import get_current_user
import app.api.admin as admin_module


class FakeConnection:
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


class FakeStore:
    def __init__(self) -> None:
        self.devices: Dict[str, Dict] = {}
        self.services: Dict[str, Dict] = {}
        self.orders: List[Dict] = []

    def now(self) -> str:
        return datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat()


class FakeCursor:
    def __init__(self, store: FakeStore) -> None:
        self.store = store
        self.connection = FakeConnection()
        self._last_row: Optional[Dict] = None
        self._last_rows: Optional[List[Dict]] = None

    def execute(self, query: str, params: Optional[List] = None) -> None:
        params = list(params or [])
        normalized = " ".join(query.strip().split())
        self._last_row = None
        self._last_rows = None

        if normalized.startswith("INSERT INTO devices"):
            new_id = str(uuid4())
            record = {
                "id": new_id,
                "label": params[0],
                "model": params[2],
                "location": params[3],
                "gpio_pin": params[4],
                "status": "ACTIVE",
                "created_at": self.store.now()
            }
            self.store.devices[new_id] = record
            self._last_row = record.copy()
        elif normalized.startswith("UPDATE devices SET"):
            device_id = params[-1]
            device = self.store.devices.get(device_id)
            if not device:
                self._last_row = None
                return

            updates = normalized.split("SET ")[1].split(" WHERE")[0].split(", ")
            updated = device.copy()
            field_map = {
                "label": "label",
                "model": "model",
                "location": "location",
                "gpio_pin": "gpio_pin",
                "status": "status"
            }

            for idx, assignment in enumerate(updates):
                column = assignment.split(" = ")[0]
                field = field_map[column]
                updated[field] = params[idx]

            self.store.devices[device_id] = updated
            self._last_row = updated.copy()
        elif normalized.startswith("SELECT label FROM devices WHERE id = %s"):
            device = self.store.devices.get(params[0])
            self._last_row = {"label": device["label"]} if device else None
        elif normalized.startswith("DELETE FROM devices WHERE id = %s"):
            device_id = params[0]
            if device_id in self.store.devices:
                del self.store.devices[device_id]
                # remove services tied to the device
                for service_id, service in list(self.store.services.items()):
                    if service["device_id"] == device_id:
                        del self.store.services[service_id]
            self._last_row = None
        elif normalized.startswith("INSERT INTO services"):
            device_id = params[0]
            if device_id not in self.store.devices:
                raise Exception("Device not found")

            new_id = str(uuid4())
            record = {
                "id": new_id,
                "device_id": device_id,
                "type": params[1],
                "price_cents": params[2],
                "fixed_minutes": params[3],
                "minutes_per_25c": params[4],
                "active": params[5],
                "created_at": self.store.now()
            }
            self.store.services[new_id] = record
            self._last_row = record.copy()
        elif normalized.startswith("UPDATE services SET"):
            service_id = params[-1]
            service = self.store.services.get(service_id)
            if not service:
                self._last_row = None
                return

            updates = normalized.split("SET ")[1].split(" WHERE")[0].split(", ")
            updated = service.copy()
            field_map = {
                "price_cents": "price_cents",
                "fixed_minutes": "fixed_minutes",
                "minutes_per_25c": "minutes_per_25c",
                "active": "active"
            }

            for idx, assignment in enumerate(updates):
                column = assignment.split(" = ")[0]
                field = field_map[column]
                updated[field] = params[idx]

            self.store.services[service_id] = updated
            self._last_row = updated.copy()
        elif normalized.startswith("SELECT type FROM services WHERE id = %s"):
            service = self.store.services.get(params[0])
            self._last_row = {"type": service["type"]} if service else None
        elif normalized.startswith("SELECT COUNT(*) as count FROM orders WHERE product_id = %s"):
            count = sum(1 for order in self.store.orders if order["product_id"] == params[0])
            self._last_row = {"count": count}
        elif normalized.startswith("DELETE FROM services WHERE id = %s"):
            service_id = params[0]
            if service_id in self.store.services:
                del self.store.services[service_id]
            self._last_row = None
        elif normalized.startswith("SELECT id, label, model, location, gpio_pin, status, created_at FROM devices WHERE id = %s"):
            device = self.store.devices.get(params[0])
            self._last_row = device.copy() if device else None
        elif normalized.startswith("SELECT id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active, created_at FROM services WHERE id = %s"):
            service = self.store.services.get(params[0])
            self._last_row = service.copy() if service else None
        else:
            raise NotImplementedError(f"Unsupported query in fake cursor: {normalized}")

    def fetchone(self) -> Optional[Dict]:
        if self._last_row is None:
            return None
        return self._last_row.copy()

    def fetchall(self) -> List[Dict]:
        rows = self._last_rows or []
        return [row.copy() for row in rows]


@pytest.fixture
def fake_store() -> FakeStore:
    return FakeStore()


@pytest.fixture
def client(fake_store: FakeStore, monkeypatch) -> TestClient:
    def override_get_db():
        cursor = FakeCursor(fake_store)
        try:
            yield cursor
        finally:
            pass

    def override_get_user():
        return {"id": str(uuid4()), "email": "admin@example.com"}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user
    monkeypatch.setattr(admin_module, "log_admin_action", lambda *args, **kwargs: None)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_device_crud_flow(client: TestClient, fake_store: FakeStore) -> None:
    create_payload = {
        "label": "Warehouse Controller",
        "public_key": "PUBLICKEY",
        "model": "Model X",
        "location": "Warehouse",
        "gpio_pin": 18
    }

    create_response = client.post("/admin/devices", json=create_payload)
    assert create_response.status_code == 200
    created_device = create_response.json()

    device_id = created_device["id"]
    assert fake_store.devices[device_id]["label"] == "Warehouse Controller"

    update_payload = {
        "label": "Warehouse Controller v2",
        "status": "MAINTENANCE",
        "location": "Warehouse - Aisle 3"
    }

    update_response = client.put(f"/admin/devices/{device_id}", json=update_payload)
    assert update_response.status_code == 200
    updated_device = update_response.json()
    assert updated_device["label"] == "Warehouse Controller v2"
    assert updated_device["status"] == "MAINTENANCE"
    assert fake_store.devices[device_id]["location"] == "Warehouse - Aisle 3"

    delete_response = client.delete(f"/admin/devices/{device_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True
    assert device_id not in fake_store.devices


def test_service_crud_and_delete_guard(client: TestClient, fake_store: FakeStore) -> None:
    device_payload = {
        "label": "Lobby Panel",
        "public_key": "PUBKEY",
        "model": "Panel-200",
        "location": "Lobby",
        "gpio_pin": 12
    }
    device_response = client.post("/admin/devices", json=device_payload)
    device_id = device_response.json()["id"]

    service_payload = {
        "device_id": device_id,
        "type": "FIXED",
        "price_cents": 500,
        "fixed_minutes": 30,
        "active": True
    }

    create_service_resp = client.post("/admin/services", json=service_payload)
    assert create_service_resp.status_code == 200
    created_service = create_service_resp.json()
    service_id = created_service["id"]
    assert fake_store.services[service_id]["price_cents"] == 500

    update_service_resp = client.put(
        f"/admin/services/{service_id}",
        json={"price_cents": 750, "active": False}
    )
    assert update_service_resp.status_code == 200
    assert update_service_resp.json()["price_cents"] == 750
    assert fake_store.services[service_id]["active"] is False

    fake_store.orders.append({"id": str(uuid4()), "product_id": service_id})

    blocked_delete = client.delete(f"/admin/services/{service_id}")
    assert blocked_delete.status_code == 400
    assert "Cannot delete service" in blocked_delete.json()["detail"]

    fake_store.orders.clear()

    delete_service_resp = client.delete(f"/admin/services/{service_id}")
    assert delete_service_resp.status_code == 200
    assert delete_service_resp.json()["success"] is True
    assert service_id not in fake_store.services


