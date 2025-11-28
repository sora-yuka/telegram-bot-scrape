run:
	docker compose up -d
	python main.py
stop:
	docker compose down -v
