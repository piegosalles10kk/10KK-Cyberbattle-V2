# ============================================
# CyberDuel API - Makefile
# ============================================

.PHONY: help install dev prod test clean docker-build docker-up docker-down logs lint format

# Cores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================
# Help
# ============================================
help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)CyberDuel API - Comandos Disponíveis$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# Setup
# ============================================
install: ## Instala dependências
	@echo "$(BLUE)Instalando dependências...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependências instaladas$(NC)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências de desenvolvimento...$(NC)"
	pip install -r requirements.txt
	pip install pytest pytest-flask pytest-cov black flake8 pylint
	@echo "$(GREEN)✓ Dependências de desenvolvimento instaladas$(NC)"

setup-env: ## Cria arquivo .env a partir do template
	@if [ ! -f .env ]; then \
		echo "$(BLUE)Criando arquivo .env...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ Arquivo .env criado. Configure as variáveis!$(NC)"; \
	else \
		echo "$(YELLOW)⚠ Arquivo .env já existe$(NC)"; \
	fi

init: install setup-env ## Inicialização completa (install + setup-env)
	@echo "$(GREEN)✓ Inicialização concluída!$(NC)"
	@echo "$(YELLOW)⚠ Configure o arquivo .env antes de iniciar$(NC)"

# ============================================
# Development
# ============================================
dev: ## Inicia servidor de desenvolvimento
	@echo "$(BLUE)Iniciando servidor de desenvolvimento...$(NC)"
	FLASK_ENV=development python api.py

prod: ## Inicia servidor de produção
	@echo "$(BLUE)Iniciando servidor de produção...$(NC)"
	FLASK_ENV=production python api.py

# ============================================
# Testing
# ============================================
test: ## Executa testes
	@echo "$(BLUE)Executando testes...$(NC)"
	pytest tests/ -v

test-coverage: ## Executa testes com cobertura
	@echo "$(BLUE)Executando testes com cobertura...$(NC)"
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Relatório de cobertura gerado em htmlcov/index.html$(NC)"

test-client: ## Executa cliente de teste interativo
	@echo "$(BLUE)Iniciando cliente de teste...$(NC)"
	python test_client.py

# ============================================
# Code Quality
# ============================================
lint: ## Executa linters (flake8, pylint)
	@echo "$(BLUE)Executando linters...$(NC)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	pylint *.py --disable=C0111,R0913,R0914

format: ## Formata código com black
	@echo "$(BLUE)Formatando código...$(NC)"
	black .
	@echo "$(GREEN)✓ Código formatado$(NC)"

check: lint test ## Executa lint + tests

# ============================================
# Docker
# ============================================
docker-build: ## Build da imagem Docker
	@echo "$(BLUE)Building imagem Docker...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Imagem construída$(NC)"

docker-up: ## Inicia containers Docker
	@echo "$(BLUE)Iniciando containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers iniciados$(NC)"
	@echo "$(YELLOW)API disponível em: http://localhost:5000$(NC)"

docker-up-monitoring: ## Inicia containers com monitoring
	@echo "$(BLUE)Iniciando containers com monitoring...$(NC)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)✓ Containers iniciados$(NC)"
	@echo "$(YELLOW)API: http://localhost:5000$(NC)"
	@echo "$(YELLOW)Prometheus: http://localhost:9090$(NC)"
	@echo "$(YELLOW)Grafana: http://localhost:3000$(NC)"

docker-up-full: ## Inicia todos os containers (API + DB + Monitoring)
	@echo "$(BLUE)Iniciando todos os containers...$(NC)"
	docker-compose --profile monitoring --profile database up -d
	@echo "$(GREEN)✓ Containers iniciados$(NC)"

docker-down: ## Para containers Docker
	@echo "$(BLUE)Parando containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers parados$(NC)"

docker-down-volumes: ## Para containers e remove volumes
	@echo "$(YELLOW)⚠ Isso irá remover todos os dados persistidos$(NC)"
	@read -p "Confirma? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ Containers e volumes removidos$(NC)"; \
	else \
		echo "$(YELLOW)Operação cancelada$(NC)"; \
	fi

docker-restart: docker-down docker-up ## Reinicia containers

docker-logs: ## Mostra logs dos containers
	docker-compose logs -f

docker-logs-api: ## Mostra logs apenas da API
	docker-compose logs -f cyberduel-api

docker-shell: ## Abre shell no container da API
	docker-compose exec cyberduel-api /bin/bash

# ============================================
# Database
# ============================================
db-migrate: ## Executa migrações do banco de dados
	@echo "$(BLUE)Executando migrações...$(NC)"
	# TODO: Implementar sistema de migração
	@echo "$(YELLOW)⚠ Migrações não implementadas ainda$(NC)"

db-reset: ## Reseta banco de dados
	@echo "$(YELLOW)⚠ Isso irá apagar todos os dados do banco$(NC)"
	@read -p "Confirma? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		docker-compose exec postgres psql -U cyberduel -c "DROP DATABASE IF EXISTS cyberduel;"; \
		docker-compose exec postgres psql -U cyberduel -c "CREATE DATABASE cyberduel;"; \
		echo "$(GREEN)✓ Banco resetado$(NC)"; \
	else \
		echo "$(YELLOW)Operação cancelada$(NC)"; \
	fi

# ============================================
# Terraform
# ============================================
terraform-init: ## Inicializa Terraform
	@echo "$(BLUE)Inicializando Terraform...$(NC)"
	cd iac/hyperv/windows-server-2022-base && terraform init
	@echo "$(GREEN)✓ Terraform inicializado$(NC)"

terraform-validate: ## Valida configuração Terraform
	@echo "$(BLUE)Validando Terraform...$(NC)"
	cd iac/hyperv/windows-server-2022-base && terraform validate
	@echo "$(GREEN)✓ Configuração válida$(NC)"

terraform-plan: ## Mostra plano de execução Terraform
	@echo "$(BLUE)Gerando plano Terraform...$(NC)"
	cd iac/hyperv/windows-server-2022-base && terraform plan

# ============================================
# Logs e Monitoring
# ============================================
logs: ## Mostra logs da aplicação
	tail -f logs/cyberduel.log

logs-clear: ## Limpa arquivos de log
	@echo "$(BLUE)Limpando logs...$(NC)"
	rm -rf logs/*.log
	@echo "$(GREEN)✓ Logs limpos$(NC)"

stats: ## Mostra estatísticas de uso
	@echo "$(BLUE)Estatísticas do sistema:$(NC)"
	@echo ""
	@echo "$(YELLOW)Containers:$(NC)"
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "$(YELLOW)Volumes:$(NC)"
	@docker volume ls --filter "name=cyberduel"
	@echo ""
	@echo "$(YELLOW)Imagens:$(NC)"
	@docker images | grep cyberduel

# ============================================
# Cleanup
# ============================================
clean: ## Remove arquivos temporários
	@echo "$(BLUE)Limpando arquivos temporários...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf temp/*
	@echo "$(GREEN)✓ Limpeza concluída$(NC)"

clean-all: clean docker-down-volumes ## Limpeza completa (temp + Docker)
	@echo "$(GREEN)✓ Limpeza completa concluída$(NC)"

# ============================================
# Utilities
# ============================================
health: ## Verifica saúde da API
	@echo "$(BLUE)Verificando saúde da API...$(NC)"
	@curl -s http://localhost:5000/api/v1/health | python -m json.tool || echo "$(RED)✗ API não está respondendo$(NC)"

list-attacks: ## Lista ataques disponíveis
	@echo "$(BLUE)Listando ataques...$(NC)"
	@curl -s http://localhost:5000/api/v1/attacks/list | python -m json.tool

backup: ## Cria backup dos resultados
	@echo "$(BLUE)Criando backup...$(NC)"
	@mkdir -p backups
	@tar -czf backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz results/ logs/
	@echo "$(GREEN)✓ Backup criado em backups/$(NC)"

# ============================================
# Default
# ============================================
.DEFAULT_GOAL := help