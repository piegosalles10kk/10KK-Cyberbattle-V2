# 📦 Guia de Instalação - CyberDuel API

Este guia detalha o processo de instalação da CyberDuel API em diferentes cenários.

## 🚨 Solução Rápida para Erro Atual

Se você está vendo o erro `No matching distribution found for flake8>=6.1.0`, siga estes passos:

### Passo 1: Atualizar o pip

```bash
# No seu venv ativo:
python -m pip install --upgrade pip

# Verificar versão (deve ser >= 24.0)
pip --version
```

### Passo 2: Instalar dependências mínimas

```bash
# Use o arquivo de requisitos mínimos
pip install -r requirements-minimal.txt
```

**OU** se quiser instalar apenas o essencial manualmente:

```bash
pip install flask==3.0.3
pip install flask-cors==5.0.0
pip install pywinrm==0.5.0
pip install requests==2.32.3
pip install python-dotenv==1.0.1
pip install python-json-logger==2.0.7
pip install jsonschema==4.23.0
pip install flask-limiter==3.8.0
```

### Passo 3: Verificar instalação

```bash
python -c "import flask; import pywinrm; import requests; print('✓ Dependências OK!')"
```

## 📋 Pré-requisitos

### Python

- **Versão mínima**: Python 3.8
- **Recomendado**: Python 3.11 ou 3.12
- **Windows**: Baixe de [python.org](https://www.python.org/downloads/)

Verifique sua versão:
```bash
python --version
```

### Terraform

```bash
# Windows (usando Chocolatey)
choco install terraform

# OU baixe manualmente de:
# https://www.terraform.io/downloads

# Verificar instalação
terraform --version
```

### Hyper-V (apenas Windows)

```powershell
# Como Administrador
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# Reinicie o computador após a instalação
```

## 🔧 Instalação Passo a Passo

### Método 1: Instalação Limpa (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/your-org/cyberduel-api.git
cd cyberduel-api

# 2. Crie ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 4. Atualize pip, setuptools e wheel
python -m pip install --upgrade pip setuptools wheel

# 5. Instale dependências mínimas primeiro
pip install -r requirements-minimal.txt

# 6. Copie o arquivo de configuração
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac

# 7. Teste a instalação
python -c "from api import app; print('✓ API pronta!')"
```

### Método 2: Instalação com Docker

```bash
# Sem necessidade de instalar Python ou dependências
# Apenas Docker Desktop

# 1. Clone o repositório
git clone https://github.com/your-org/cyberduel-api.git
cd cyberduel-api

# 2. Configure ambiente
copy .env.example .env
# Edite o .env conforme necessário

# 3. Build e inicie
docker-compose up -d

# 4. Verifique logs
docker-compose logs -f
```

## 🔍 Troubleshooting

### Erro: "pip install falha"

**Problema**: Versão antiga do pip

**Solução**:
```bash
# Atualize pip primeiro
python -m pip install --upgrade pip

# Depois reinstale
pip install -r requirements-minimal.txt
```

### Erro: "No module named 'flask'"

**Problema**: Ambiente virtual não ativo ou dependências não instaladas

**Solução**:
```bash
# 1. Certifique-se que o venv está ativo
# Você deve ver (venv) no prompt

# 2. Se não estiver, ative:
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# 3. Reinstale dependências
pip install flask flask-cors pywinrm requests
```

### Erro: "pywinrm installation failed"

**Problema**: Faltam compiladores C++ no Windows

**Solução**:
```bash
# Instale Microsoft C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# OU use wheel pré-compilado:
pip install --only-binary :all: pywinrm
```

### Erro: "Permission denied" ao criar venv

**Problema**: Permissões de execução

**Solução Windows**:
```powershell
# Como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solução Linux/Mac**:
```bash
chmod +x venv/bin/activate
```

### Erro: "Terraform not found"

**Problema**: Terraform não está no PATH

**Solução Windows**:
```powershell
# 1. Baixe terraform.exe
# 2. Coloque em C:\Windows\System32
# OU adicione ao PATH manualmente
```

**Solução Linux/Mac**:
```bash
# Baixe e instale
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### Erro: "Hyper-V não disponível"

**Problema**: Hyper-V não está habilitado

**Solução**:
```powershell
# Como Administrador
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Restart-Computer
```

**Nota**: Hyper-V requer Windows 10/11 Pro ou Enterprise

## 🎯 Verificação da Instalação

Execute este script para verificar tudo:

```python
# check_install.py
import sys

def check_python():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print("✓ Python versão OK:", sys.version.split()[0])
        return True
    else:
        print("✗ Python versão insuficiente:", sys.version.split()[0])
        return False

def check_modules():
    required = ['flask', 'pywinrm', 'requests', 'dotenv', 'jsonschema']
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"✓ {module} instalado")
        except ImportError:
            print(f"✗ {module} NÃO instalado")
            missing.append(module)
    
    return len(missing) == 0

def check_terraform():
    import subprocess
    try:
        result = subprocess.run(['terraform', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✓ {version}")
            return True
    except FileNotFoundError:
        print("✗ Terraform NÃO encontrado no PATH")
    return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("VERIFICAÇÃO DE INSTALAÇÃO - CyberDuel API")
    print("="*50 + "\n")
    
    checks = [
        ("Python", check_python),
        ("Módulos Python", check_modules),
        ("Terraform", check_terraform)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("✓ TODAS AS VERIFICAÇÕES PASSARAM!")
        print("Você está pronto para usar a CyberDuel API")
    else:
        print("✗ ALGUMAS VERIFICAÇÕES FALHARAM")
        print("Revise as mensagens acima e corrija os problemas")
    print("="*50 + "\n")
```

Execute:
```bash
python check_install.py
```

## 📦 Estrutura de Diretórios Após Instalação

```
10KK-CyberDuel V2/
├── venv/                          # Ambiente virtual Python
├── api.py                         # API principal
├── orchestrator.py                # Orquestrador
├── attack_database.py             # Banco de ataques
├── terraform_manager.py           # Gerenciador Terraform
├── attack_executor.py             # Executor de ataques
├── config.py                      # Configurações
├── .env                           # Variáveis de ambiente (CRIAR)
├── .env.example                   # Template de configuração
├── requirements.txt               # Dependências (todas)
├── requirements-minimal.txt       # Dependências mínimas
├── iac/                          # Infraestrutura
│   └── hyperv/
│       └── windows-server-2022-base/
│           ├── main.tf
│           ├── variables.tf
│           └── modules/
├── logs/                         # Logs (será criado)
├── temp/                         # Arquivos temporários (será criado)
└── results/                      # Resultados dos testes (será criado)
```

## 🚀 Próximos Passos

Após a instalação bem-sucedida:

1. **Configure o arquivo .env**
   ```bash
   notepad .env  # Windows
   nano .env     # Linux
   ```

2. **Configure VM base do Hyper-V**
   - Veja: [QUICKSTART.md](QUICKSTART.md#preparar-vm-base-hyper-v)

3. **Inicie a API**
   ```bash
   python api.py
   ```

4. **Teste a API**
   ```bash
   # Em outro terminal
   curl http://localhost:5000/api/v1/health
   ```

## 📞 Suporte

Se você ainda tiver problemas após seguir este guia:

1. Verifique os logs em `logs/cyberduel.log`
2. Consulte [QUICKSTART.md](QUICKSTART.md#troubleshooting)
3. Abra uma issue no GitHub com:
   - Versão do Python (`python --version`)
   - Versão do pip (`pip --version`)
   - Sistema operacional
   - Mensagem de erro completa
   - Output de `pip list`

## 📚 Referências

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [pip Documentation](https://pip.pypa.io/)
- [Terraform Installation](https://learn.hashicorp.com/tutorials/terraform/install-cli)
- [Hyper-V on Windows](https://docs.microsoft.com/en-us/virtualization/hyper-v-on-windows/)