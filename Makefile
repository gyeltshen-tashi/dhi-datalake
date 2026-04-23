.PHONY: help deploy update restart restart-infra restart-api restart-agents logs-api logs-agents logs-infra status

help:
	@echo "DHI Datalake - Available Commands"
	@echo "----------------------------------"
	@echo "make deploy         Pull latest code and restart all services"
	@echo "make update         Pull latest code only, no restart"
	@echo "make restart        Restart all services"
	@echo "make restart-infra  Restart infrastructure (Docker containers)"
	@echo "make restart-api    Restart API service"
	@echo "make restart-agents Restart agents service"
	@echo "make logs-infra     Follow infrastructure logs"
	@echo "make logs-api       Follow API logs"
	@echo "make logs-agents    Follow agents logs"
	@echo "make status         Show status of all services"

deploy: update restart

update:
	git -C /home/lake/dhi-datalake pull
	cp /home/lake/dhi-datalake/infrastructure/docker-compose.yml /home/lake/datalake/docker-compose.yml

restart: restart-infra restart-api restart-agents

restart-infra:
	sudo systemctl restart datalake

restart-api:
	sudo systemctl restart dhi-api

restart-agents:
	sudo systemctl restart dhi-agents

logs-infra:
	sudo docker compose -f /home/lake/datalake/docker-compose.yml logs -f

logs-api:
	sudo journalctl -u dhi-api -f

logs-agents:
	sudo journalctl -u dhi-agents -f

status:
	@echo "=== Infrastructure ==="
	@sudo systemctl status datalake --no-pager
	@echo ""
	@echo "=== API ==="
	@sudo systemctl status dhi-api --no-pager
	@echo ""
	@echo "=== Agents ==="
	@sudo systemctl status dhi-agents --no-pager
	@echo ""
	@echo "=== Docker Containers ==="
	@sudo docker ps
