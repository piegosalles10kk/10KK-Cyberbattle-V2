# CyberDuel API - Sistema de Testes EDR Automatizados

API Flask para execução automatizada de testes de detecção e resposta de EDRs usando técnicas MITRE ATT&CK.

## 📋 Índice

- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Endpoints](#endpoints)
- [Payload do Teste](#payload-do-teste)
- [Banco de Ataques](#banco-de-ataques)
- [Logs em Tempo Real](#logs-em-tempo-real)
- [Exemplos de Uso](#exemplos-de-uso)

## 🏗️ Arquitetura

```
CyberDuel API
├── api.py                  # API Flask principal
├── orchestrator.py         # Orquestrador de testes
├── attack_database.py      # Banco MITRE ATT&CK
├── terraform_manager.py    # Gerenciador Terraform
├── attack_executor.py      # Executor WinRM
└── iac/                    # Infraestrutura como Código
    ├── hyperv/
    │   ├── windows-server-2022-base/
    │   └── windows-10-pro/
    └── azure/
        └── ...
```

## 📦 Instalação

### Pré-requisitos

```bash
# Python 3.8+
pip install -r requirements.txt

# Terraform instalado e no PATH
terraform --version

# Para Hyper-V (Windows)
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### Dependências

```txt
flask>=2.3.0
pywinrm>=0.4.3
requests>=2.31.0
```

### Iniciar a API

```bash
python api.py
```

A API estará disponível em `http://localhost:5000`

## 🔌 Endpoints

### 1. Executar Teste CyberDuel

**POST** `/api/v1/cyberduel/execute`

Executa um teste completo com streaming de logs em tempo real.

**Headers:**
```
Content-Type: application/json
```

**Response:**
- Content-Type: `text/event-stream` (Server-Sent Events)
- Cada evento contém um objeto JSON com o log

### 2. Listar Ataques

**GET** `/api/v1/attacks/list`

Retorna todos os ataques disponíveis no banco de dados.

**Response:**
```json
{
  "status": "success",
  "total": 17,
  "attacks": [...]
}
```

### 3. Detalhes de Ataque

**GET** `/api/v1/attacks/{ttp_id}`

Retorna detalhes de um ataque específico.

**Exemplo:** `/api/v1/attacks/T1059.001`

### 4. Health Check

**GET** `/api/v1/health`

Verifica o status da API.

## 📝 Payload do Teste

### Estrutura Completa

```json
{
    "test_id": "T-001-CROWDSTRIKE-WIN",
    "test_name": "Round 1 - CrowdStrike vs PowerShell Abuse",
    "cloud_provider": "hyperv",
    "os_template": "windows-server-2022-base",
    
    "vm_config": {
        "vm_cpu": 4,
        "vm_ram_mb": 4096,
        "vm_switch_name": "Default Switch",
        "base_vhdx_path": "D:\\CyberDuel\\VM-BASES\\Win2022-Limpo.vhdx",
        "admin_user": "svc-adm-test",
        "admin_password": "SenhaSeguraDoSistema"
    },
    
    "edr_config": {
        "vendor_name": "CrowdStrike Falcon",
        "edr_token": "S3CR3T-T0K3N-12345",
        "cid_value": "CID-AABBCCDD",
        "installation_script_base64": "JVdGcnRpb24gYSBzdGFu..."
    },
    
    "attack_config": {
        "ttp_id": "T1059.001",
        "ttp_name": "PowerShell Execution",
        "attack_script_path": "/path/to/attack.ps1",
        "validation_check_command": "Get-Item C:\\Temp\\artifact.txt"
    }
}
```

### Campos Obrigatórios

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `test_id` | string | Identificador único do teste |
| `test_name` | string | Nome descritivo do teste |
| `cloud_provider` | string | Provider do Terraform (`hyperv`, `azure`, `aws`) |
| `os_template` | string | Template do sistema operacional |
| `vm_config` | object | Configurações das VMs |

### Campos Opcionais

- `edr_config`: Configuração do EDR a ser instalado
- `attack_config`: Configuração específica do ataque (se omitido, usa sequência padrão)

## 🎯 Banco de Ataques

O sistema inclui 17 ataques pré-configurados baseados no MITRE ATT&CK:

### Táticas Cobertas

#### Execution (TA0002)
- **T1059.001** - PowerShell Execution
- **T1059.003** - Windows Command Shell
- **T1047** - Windows Management Instrumentation

#### Defense Evasion (TA0005)
- **T1027** - Obfuscated Files or Information
- **T1055** - Process Injection
- **T1070.001** - Clear Windows Event Logs

#### Persistence (TA0003)
- **T1547.001** - Registry Run Keys
- **T1053.005** - Scheduled Task

#### Credential Access (TA0006)
- **T1003.001** - LSASS Memory Dump
- **T1552.001** - Credentials in Files

#### Lateral Movement (TA0008)
- **T1021.001** - Remote Desktop Protocol
- **T1021.006** - Windows Remote Management

#### Collection (TA0009)
- **T1560.001** - Archive via Utility

#### Exfiltration (TA0010)
- **T1041** - Exfiltration Over C2 Channel

#### Impact (TA0040)
- **T1486** - Data Encrypted for Impact (Ransomware)
- **T1490** - Inhibit System Recovery

### Bibliotecas Alternativas

Para um banco de dados mais completo, considere:

```bash
# MITRE ATT&CK oficial
pip install mitreattack-python

# pyattck - Interface mais amigável
pip install pyattck
```

## 📊 Logs em Tempo Real

A API retorna logs via **Server-Sent Events (SSE)**.

### Formato dos Logs

Cada evento tem a estrutura:

```json
{
    "timestamp": "2025-10-15T14:30:00.000Z",
    "level": "INFO|SUCCESS|WARNING|ERROR|DEBUG",
    "message": "Mensagem descritiva",
    "data": {
        "key": "value"
    }
}
```

### Evento Final

Quando o teste termina, é enviado:

```json
{
    "status": "completed"
}
```

## 🚀 Exemplos de Uso

### 1. Teste Simples (Sem EDR)

```bash
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "T-SIMPLE-001",
    "test_name": "Teste Básico de PowerShell",
    "cloud_provider": "hyperv",
    "os_template": "windows-server-2022-base",
    "vm_config": {
        "vm_cpu": 2,
        "vm_ram_mb": 4096,
        "vm_switch_name": "Default Switch",
        "base_vhdx_path": "C:\\HyperV-Disks\\VM-BASE.vhdx",
        "admin_user": "adm",
        "admin_password": "adm123"
    }
}'
```

### 2. Teste com EDR Específico

```bash
curl -X POST http://localhost:5000/api/v1/cyberduel/execute \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "T-EDR-001",
    "test_name": "CrowdStrike vs Lateral Movement",
    "cloud_provider": "hyperv",
    "os_template": "windows-10-pro",
    "vm_config": {
        "vm_cpu": 4,
        "vm_ram_mb": 8192,
        "vm_switch_name": "Default Switch",
        "base_vhdx_path": "D:\\VMs\\Win10-Base.vhdx",
        "admin_user": "svc-test",
        "admin_password": "P@ssw0rd123"
    },
    "edr_config": {
        "vendor_name": "CrowdStrike Falcon",
        "edr_token": "TOKEN-12345",
        "installation_script_base64": "cG93ZXJzaGVsbC5leGUgLUNvbW1hbmQgIkRvd25sb2FkLUZpbGUgaHR0cDovL2Vkci5jb20vaW5zdGFsbC5wczEi"
    },
    "attack_config": {
        "ttp_id": "T1021.006"
    }
}'
```

### 3. Cliente Python com SSE

```python
import requests
import json

def execute_test():
    payload = {
        "test_id": "T-PYTHON-001",
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
    
    # Processar logs em tempo real
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data = json.loads(line_str[6:])
                
                if data.get('status') == 'completed':
                    print("\n✅ Teste concluído!")
                    break
                
                print(f"[{data['level']}] {data['message']}")
                if 'winner' in data.get('data', {}):
                    print(f"🏆 Vencedor: {data['data']['winner']}")

if __name__ == "__main__":
    execute_test()
```

### 4. Cliente JavaScript (Browser)

```javascript
async function executeCyberDuelTest() {
    const payload = {
        test_id: "T-JS-001",
        test_name: "Teste via JavaScript",
        cloud_provider: "hyperv",
        os_template: "windows-server-2022-base",
        vm_config: {
            vm_cpu: 2,
            vm_ram_mb: 4096,
            vm_switch_name: "Default Switch",
            base_vhdx_path: "C:\\VMs\\Base.vhdx",
            admin_user: "adm",
            admin_password: "adm123"
        }
    };
    
    const response = await fetch('http://localhost:5000/api/v1/cyberduel/execute', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.substring(6));
                
                if (data.status === 'completed') {
                    console.log('✅ Teste concluído!');
                    return;
                }
                
                console.log(`[${data.level}] ${data.message}`);
            }
        }
    }
}

executeCyberDuelTest();
```

## 🔒 Segurança

### Recomendações de Produção

1. **Autenticação**: Adicione autenticação JWT ou API Keys
2. **Rate Limiting**: Implemente limites de requisições
3. **Validação**: Valide rigorosamente todos os inputs
4. **Isolamento**: Execute em ambiente isolado/sandboxed
5. **Logs**: Implemente auditoria completa
6. **HTTPS**: Use TLS em produção

### Variáveis de Ambiente

```bash
export CYBERDUEL_SECRET_KEY="sua-chave-secreta"
export CYBERDUEL_DEBUG="False"
export CYBERDUEL_MAX_WORKERS="5"
```

## 📈 Métricas e Pontuação

### Sistema de Pontos

- **Detecção**: +10 pontos
- **Bloqueio**: +20 pontos
- **Resposta Rápida** (< 1s): +5 pontos
- **Bônus por Severidade**:
  - LOW: +5
  - MEDIUM: +10
  - HIGH: +15
  - CRITICAL: +20

### Cálculo do Vencedor

1. **HP Final**: 100 - Dano Recebido
2. **Pontuação Total**: HP Final + Pontos de Defesa
3. **Desempate**: Maior pontuação de defesa

## 🐛 Troubleshooting

### Erro: "Diretório Terraform não encontrado"

Verifique a estrutura de diretórios:
```bash
mkdir -p iac/hyperv/windows-server-2022-base
```

### Erro: "WinRM Connection Failed"

1. Verifique se o WinRM está habilitado na VM
2. Verifique credenciais
3. Teste manualmente: `Test-WSMan -ComputerName <IP>`

### Erro: "Terraform Apply Timeout"

Aumente o timeout em `terraform_manager.py`:
```python
timeout=1200  # 20 minutos
```

## 📚 Referências

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [WinRM Protocol](https://docs.microsoft.com/en-us/windows/win32/winrm/)
- [Flask SSE](https://flask.palletsprojects.com/en/2.3.x/patterns/streaming/)

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais e de teste.

## ⚠️ Aviso Legal

**USE APENAS EM AMBIENTES DE TESTE CONTROLADOS**

Este sistema executa técnicas de ataque reais que podem ser detectadas como maliciosas por EDRs e outras ferramentas de segurança. Use apenas em ambientes isolados e com permissão apropriada.