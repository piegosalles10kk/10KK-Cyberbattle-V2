# 🚀 Guia de Início Rápido - CyberDuel API

Este guia ajudará você a colocar a CyberDuel API funcionando em menos de 10 minutos.

## 📋 Pré-requisitos

### Opção 1: Instalação Local

- **Python 3.8+** instalado
- **Terraform** instalado e no PATH
- **Hyper-V** habilitado (apenas Windows)
- **Git** para clonar o repositório

### Opção 2: Docker (Recomendado)

- **Docker Desktop** ou **Docker Engine** + **Docker Compose**

## 🎯 Instalação Rápida

### Método 1: Docker (Mais Rápido) ⚡

```bash
# 1. Clone o repositório
git clone https://github.com/your-org/cyberduel-api.git
cd cyberduel-api

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Inicie os containers
make docker-up
# OU
docker-compose up -d

# 4. Verifique se está funcionando
curl http://localhost:5000/api/v1/health
```

**Pronto!** A API está rodando em `http://localhost:5000`

### Método 2: Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/your-org/cyberduel-api.git
cd cyberduel-api

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OU
.\venv\Scripts\activate  # Windows

# 3. Instale dependências
make install
# OU
pip install -r requirements.txt

# 4. Configure ambiente
make setup-env
# Edite o arquivo .env criado

# 5. Inicie a API
make dev
# OU
python api.py
```

## 🔧 Configuração Básica

### 1. Arquivo .env

As configurações mínimas necessárias:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=mude-isto-em-producao

# Terraform
TERRAFORM_BASE_DIR=./iac

# Hyper-V (apenas Windows)
HYPERV_HOST=127.0.0.1
HYPERV_USER=seu-usuario-admin
HYPERV_PASSWORD=sua-senha
```

### 2. Estrutura de Diretórios

Certifique-se de ter a estrutura:

```
cyberduel-api/
├── api.py
├── orchestrator.py
├── attack_database.py
├── terraform_manager.py
├── attack_executor.py
├── config.py
├── iac/
│   └── hyperv/
│       └── windows-server-2022-base/
│           ├── main.tf
│           ├── variables.tf
│           └── modules/
└── logs/
```

### 3. Preparar VM Base (Hyper-V)

```powershell
# Criar VM base limpa
# 1. Instale Windows Server 2022
# 2. Configure WinRM
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force

# 3. Crie snapshot/checkpoint
# 4. Exporte como VHDX base
```

## 🎮 Primeiro Teste

### Via Cliente Python

```bash
# Inicie o cliente interativo
make test-client
# OU
python test_client.py

# Siga o menu para executar teste básico
```

### Via cURL

```bash
# 1. Verificar saúde
curl http://localhost:5000/api/v1/health

# 2. Listar ataques disponíveis
curl http://localhost:5000/api/v1/attacks/list | jq

# 3. Executar teste básico
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "TEST-001",
    "test_name": "Primeiro Teste",
    "cloud_provider": "hyperv",
    "os_template": "windows-server-2022-base",
    "vm_config": {
      "vm_cpu": 2,
      "vm_ram_mb": 4096,
      "vm_switch_name": "Default Switch",
      "base_vhdx_path": "C:\\VMs\\Base.vhdx",
      "admin_user": "adm",
      "admin_password": "adm123"
    }
  }'
```

### Via Python Script

```python
import requests
import json

payload = {
    "test_id": "TEST-PYTHON-001",
    "test_name": "Teste via Python",
    "cloud_provider": "hyperv",
    "os_template": "windows-server-2022-base",
    "vm_config": {
        "vm_cpu": 2,
        "vm_ram_mb": 4096,
        "vm_switch_name": "Default Switch",
        "base_vhdx_path": "C:\\VMs\\Base.vhdx",
        "admin_user": "adm",
        "admin_password": "adm123"
    }
}

response = requests.post(
    "http://localhost:5000/api/v1/cyberduel/execute",
    json=payload,
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## 📊 Monitoramento (Opcional)

Para habilitar monitoramento com Prometheus e Grafana:

```bash
# Inicie com profile de monitoring
make docker-up-monitoring

# Acesse:
# - API: http://localhost:5000
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)
```

## 🔍 Troubleshooting

### Problema: API não inicia

```bash
# Verifique logs
make logs
# OU
docker-compose logs cyberduel-api

# Verifique porta em uso
netstat -an | grep 5000
```

### Problema: Terraform falha

```bash
# Valide configuração
make terraform-validate

# Inicialize novamente
make terraform-init

# Verifique credenciais Hyper-V
winrm get winrm/config
```

### Problema: WinRM não conecta

```powershell
# Na VM base, verifique:
Test-WSMan

# Habilite novamente se necessário
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
Restart-Service WinRM
```

### Problema: Container não sobe

```bash
# Reconstruir imagem
make docker-build

# Verificar logs detalhados
docker-compose logs -f --tail=100

# Remover e recriar
make docker-down
make docker-up
```

## 📚 Próximos Passos

1. **Explore os ataques disponíveis**
   ```bash
   make list-attacks
   ```

2. **Execute testes customizados**
   - Veja exemplos em `example_payloads.json`
   - Consulte a documentação completa em `README.md`

3. **Configure EDR real**
   - Adicione scripts de instalação no payload
   - Teste detecção e resposta

4. **Automatize testes**
   - Crie pipelines CI/CD
   - Integre com ferramentas de segurança

## 🆘 Suporte

- **Documentação completa**: `README.md`
- **Exemplos de payloads**: `example_payloads.json`
- **Base de ataques**: Execute `GET /api/v1/attacks/list`
- **Issues**: Abra uma issue no GitHub
- **Discord**: [Link para comunidade]

## ⚡ Comandos Úteis

```bash
# Ver todos os comandos disponíveis
make help

# Executar testes
make test

# Verificar código
make lint

# Formatar código
make format

# Criar backup
make backup

# Limpar arquivos temporários
make clean

# Parar tudo
make docker-down
```

## 🎓 Tutoriais por Caso de Uso

### Caso 1: Testar PowerShell Abuse

```bash
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "test_id": "PS-001",
  "test_name": "PowerShell Abuse Test",
  "cloud_provider": "hyperv",
  "os_template": "windows-server-2022-base",
  "vm_config": {
    "vm_cpu": 2,
    "vm_ram_mb": 4096,
    "vm_switch_name": "Default Switch",
    "base_vhdx_path": "C:\\VMs\\Base.vhdx",
    "admin_user": "adm",
    "admin_password": "adm123"
  },
  "attack_config": {
    "ttp_id": "T1059.001"
  }
}
EOF
```

### Caso 2: Testar com EDR (CrowdStrike)

```bash
# Primeiro, encode seu script de instalação:
echo 'Install-CrowdStrike.ps1' | base64

# Depois, use no payload:
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "EDR-001",
    "test_name": "CrowdStrike Test",
    "cloud_provider": "hyperv",
    "os_template": "windows-10-pro",
    "vm_config": {...},
    "edr_config": {
      "vendor_name": "CrowdStrike",
      "edr_token": "YOUR-TOKEN",
      "installation_script_base64": "BASE64-ENCODED-SCRIPT"
    }
  }'
```

### Caso 3: Sequência Completa de Ataques

```bash
# Sem especificar TTP, executa sequência padrão
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "FULL-001",
    "test_name": "Full Attack Sequence",
    "cloud_provider": "hyperv",
    "os_template": "windows-server-2022-base",
    "vm_config": {...}
  }'
```

---

**🎉 Parabéns!** Você está pronto para começar a testar EDRs com a CyberDuel API!

Para documentação completa, consulte: [README.md](README.md)