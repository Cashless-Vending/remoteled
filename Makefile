.PHONY: help build app-up app-down logs logs-iot logs-web clean

PLATFORM := linux/arm64

help:
	@echo "RemoteLED Docker Commands:"
	@echo "  make build     - Build all containers for Raspberry Pi 4"
	@echo "  make app-up    - Start all services (detached)"
	@echo "  make app-down  - Stop all services"
	@echo "  make logs      - View all logs (follow mode)"
	@echo "  make logs-iot  - View BLE+GPIO service logs"
	@echo "  make logs-web  - View web kiosk logs"
	@echo "  make clean     - Stop and remove all containers/volumes"

build:
	@echo "Building containers for $(PLATFORM)..."
	docker compose build

app-up:
	@echo "Starting RemoteLED services..."
	docker compose up -d
	@echo "✓ Services running!"
	@echo "  - Web: http://localhost"
	@echo "  - BLE: active on host Bluetooth"

app-down:
	@echo "Stopping RemoteLED services..."
	docker compose down

logs:
	docker compose logs -f

logs-iot:
	docker compose logs -f iot-peripheral

logs-web:
	docker compose logs -f web-kiosk

clean:
	@echo "Cleaning up containers and volumes..."
	docker compose down -v
	@echo "✓ Cleanup complete"
