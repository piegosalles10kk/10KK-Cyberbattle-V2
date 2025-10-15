# Multi-stage build para otimizar tamanho da imagem
FROM python:3.11-slim as builder

# Instalar dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Imagem final
# ============================================
FROM python:3.11-slim

# Metadados
LABEL maintainer="CyberDuel Team"
LABEL description="CyberDuel API - Automated EDR Testing with MITRE ATT&CK"
LABEL version="1.0.0"

# Instalar Terraform (necessário para orquestração)
ARG TERRAFORM_VERSION=1.6.0
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    unzip \
    && wget -q https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/bin/ \
    && rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && apt-get remove -y wget unzip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 cyberduel && \
    mkdir -p /app /app/logs /app/temp /app/results && \
    chown -R cyberduel:cyberduel /app

# Configurar diretório de trabalho
WORKDIR /app

# Copiar dependências Python do builder
COPY --from=builder /root/.local /home/cyberduel/.local

# Copiar código da aplicação
COPY --chown=cyberduel:cyberduel api.py .
COPY --chown=cyberduel:cyberduel orchestrator.py .
COPY --chown=cyberduel:cyberduel attack_database.py .
COPY --chown=cyberduel:cyberduel terraform_manager.py .
COPY --chown=cyberduel:cyberduel attack_executor.py .
COPY --chown=cyberduel:cyberduel config.py .
COPY --chown=cyberduel:cyberduel .env.example .env

# Copiar diretório de infraestrutura (Terraform)
COPY --chown=cyberduel:cyberduel iac/ ./iac/

# Atualizar PATH para incluir binários do usuário
ENV PATH=/home/cyberduel/.local/bin:$PATH

# Mudar para usuário não-root
USER cyberduel

# Expor porta
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health').raise_for_status()"

# Comando de inicialização
CMD ["python", "api.py"]