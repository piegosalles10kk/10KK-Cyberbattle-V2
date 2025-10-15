#!/usr/bin/env python
"""
Script de verificação de instalação da CyberDuel API
Verifica se todas as dependências e ferramentas necessárias estão instaladas
"""

import sys
import subprocess
import os
from pathlib import Path

# Cores para output (ANSI)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    """Imprime informação"""
    print(f"  {text}")

def check_python_version():
    """Verifica versão do Python"""
    print(f"\n{YELLOW}[Verificando Python]{RESET}")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} instalado")
        return True
    else:
        print_error(f"Python {version_str} - Versão mínima requerida: 3.8")
        return False

def check_pip_version():
    """Verifica versão do pip"""
    print(f"\n{YELLOW}[Verificando pip]{RESET}")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            pip_version = result.stdout.strip()
            print_success(pip_version)
            
            # Extrair número da versão
            version_num = pip_version.split()[1]
            major_version = int(version_num.split('.')[0])
            
            if major_version < 20:
                print_warning("Versão do pip está desatualizada")
                print_info("Execute: python -m pip install --upgrade pip")
                return True  # Não falhar, apenas avisar
            
            return True
        else:
            print_error("Falha ao verificar pip")
            return False
    except Exception as e:
        print_error(f"Erro ao verificar pip: {e}")
        return False

def check_required_modules():
    """Verifica módulos Python obrigatórios"""
    print(f"\n{YELLOW}[Verificando Módulos Python Obrigatórios]{RESET}")
    
    required = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'winrm': 'pywinrm',
        'requests': 'Requests',
        'dotenv': 'python-dotenv',
        'jsonschema': 'jsonschema',
        'flask_limiter': 'Flask-Limiter'
    }
    
    missing = []
    
    for module_name, display_name in required.items():
        try:
            __import__(module_name)
            print_success(f"{display_name} instalado")
        except ImportError:
            print_error(f"{display_name} NÃO instalado")
            missing.append(display_name)
    
    if missing:
        print_warning(f"\nMódulos faltando: {', '.join(missing)}")
        print_info("Execute: pip install -r requirements-minimal.txt")
        return False
    
    return True

def check_optional_modules():
    """Verifica módulos Python opcionais"""
    print(f"\n{YELLOW}[Verificando Módulos Opcionais]{RESET}")
    
    optional = {
        'pytest': 'pytest (testes)',
        'black': 'black (formatação)',
        'prometheus_client': 'prometheus-client (monitoring)'
    }
    
    for module_name, display_name in optional.items():
        try:
            __import__(module_name)
            print_success(f"{display_name} instalado")
        except ImportError:
            print_info(f"{display_name} não instalado (opcional)")
    
    return True

def check_terraform():
    """Verifica instalação do Terraform"""
    print(f"\n{YELLOW}[Verificando Terraform]{RESET}")
    
    try:
        result = subprocess.run(
            ['terraform', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_success(version_line)
            return True
        else:
            print_error("Terraform instalado mas não funcional")
            return False
    except FileNotFoundError:
        print_error("Terraform NÃO encontrado no PATH")
        print_info("Baixe em: https://www.terraform.io/downloads")
        return False
    except Exception as e:
        print_error(f"Erro ao verificar Terraform: {e}")
        return False

def check_terraform_config():
    """Verifica configuração do Terraform"""
    print(f"\n{YELLOW}[Verificando Configuração Terraform]{RESET}")
    
    terraform_dirs = [
        Path('./iac/hyperv/windows-server-2022-base'),
        Path('./infra_cyberduel')
    ]
    
    found = False
    for tf_dir in terraform_dirs:
        if tf_dir.exists():
            print_success(f"Diretório Terraform encontrado: {tf_dir}")
            
            # Verificar arquivos essenciais
            main_tf = tf_dir / 'main.tf'
            if main_tf.exists():
                print_success("  ✓ main.tf encontrado")
            else:
                print_error("  ✗ main.tf não encontrado")
            
            found = True
            break
    
    if not found:
        print_error("Nenhum diretório Terraform encontrado")
        print_info("Esperado: ./iac/hyperv/windows-server-2022-base/")
        return False
    
    return True

def check_environment_file():
    """Verifica arquivo .env"""
    print(f"\n{YELLOW}[Verificando Arquivo de Configuração]{RESET}")
    
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print_success(".env encontrado")
        
        # Verificar se tem conteúdo
        content = env_file.read_text()
        if len(content) > 50:
            print_success("  ✓ Arquivo contém configurações")
        else:
            print_warning("  ⚠ Arquivo parece vazio ou incompleto")
        
        return True
    else:
        print_warning(".env NÃO encontrado")
        
        if env_example.exists():
            print_info("Execute: copy .env.example .env (Windows)")
            print_info("    OU: cp .env.example .env (Linux/Mac)")
        else:
            print_error(".env.example também não encontrado")
        
        return False

def check_directory_structure():
    """Verifica estrutura de diretórios"""
    print(f"\n{YELLOW}[Verificando Estrutura de Diretórios]{RESET}")
    
    required_files = [
        'api.py',
        'orchestrator.py',
        'attack_database.py',
        'terraform_manager.py',
        'attack_executor.py',
        'config.py'
    ]
    
    missing_files = []
    for filename in required_files:
        if Path(filename).exists():
            print_success(f"{filename} encontrado")
        else:
            print_error(f"{filename} NÃO encontrado")
            missing_files.append(filename)
    
    if missing_files:
        print_error(f"\nArquivos essenciais faltando: {', '.join(missing_files)}")
        return False
    
    # Criar diretórios se não existirem
    dirs_to_create = ['logs', 'temp', 'results']
    for dirname in dirs_to_create:
        dir_path = Path(dirname)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print_success(f"Diretório '{dirname}/' criado")
            except Exception as e:
                print_error(f"Erro ao criar '{dirname}/': {e}")
        else:
            print_info(f"Diretório '{dirname}/' já existe")
    
    return True

def check_hyperv():
    """Verifica se Hyper-V está disponível (Windows apenas)"""
    print(f"\n{YELLOW}[Verificando Hyper-V]{RESET}")
    
    if sys.platform != 'win32':
        print_info("Sistema não é Windows - Hyper-V não aplicável")
        return True
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'Enabled' in result.stdout:
            print_success("Hyper-V está habilitado")
            return True
        else:
            print_warning("Hyper-V não parece estar habilitado")
            print_info("Execute como Admin: Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All")
            return False
    except Exception as e:
        print_warning(f"Não foi possível verificar Hyper-V: {e}")
        return True  # Não falhar a verificação

def run_all_checks():
    """Executa todas as verificações"""
    print_header("VERIFICAÇÃO DE INSTALAÇÃO - CyberDuel API")
    
    checks = [
        ("Python Version", check_python_version, True),
        ("pip Version", check_pip_version, True),
        ("Módulos Obrigatórios", check_required_modules, True),
        ("Módulos Opcionais", check_optional_modules, False),
        ("Terraform", check_terraform, True),
        ("Config Terraform", check_terraform_config, True),
        ("Arquivo .env", check_environment_file, True),
        ("Estrutura de Diretórios", check_directory_structure, True),
        ("Hyper-V", check_hyperv, False)
    ]
    
    results = []
    critical_failed = False
    
    for name, check_func, is_critical in checks:
        try:
            result = check_func()
            results.append((name, result, is_critical))
            
            if is_critical and not result:
                critical_failed = True
        except Exception as e:
            print_error(f"Erro ao verificar {name}: {e}")
            results.append((name, False, is_critical))
            if is_critical:
                critical_failed = True
    
    # Resumo final
    print_header("RESUMO DA VERIFICAÇÃO")
    
    critical_passed = sum(1 for _, result, is_critical in results if is_critical and result)
    critical_total = sum(1 for _, _, is_critical in results if is_critical)
    optional_passed = sum(1 for _, result, is_critical in results if not is_critical and result)
    optional_total = sum(1 for _, _, is_critical in results if not is_critical)
    
    print(f"\n{YELLOW}Verificações Obrigatórias:{RESET} {critical_passed}/{critical_total} passaram")
    print(f"{YELLOW}Verificações Opcionais:{RESET} {optional_passed}/{optional_total} passaram\n")
    
    if not critical_failed:
        print(f"{GREEN}{'='*60}{RESET}")
        print(f"{GREEN}✓ TODAS AS VERIFICAÇÕES CRÍTICAS PASSARAM!{RESET}")
        print(f"{GREEN}Você está pronto para usar a CyberDuel API{RESET}")
        print(f"{GREEN}{'='*60}{RESET}\n")
        
        print(f"{BLUE}Próximos passos:{RESET}")
        print("  1. Configure o arquivo .env")
        print("  2. Inicie a API: python api.py")
        print("  3. Teste: curl http://localhost:5000/api/v1/health\n")
        
        return 0
    else:
        print(f"{RED}{'='*60}{RESET}")
        print(f"{RED}✗ ALGUMAS VERIFICAÇÕES CRÍTICAS FALHARAM{RESET}")
        print(f"{RED}Revise as mensagens acima e corrija os problemas{RESET}")
        print(f"{RED}{'='*60}{RESET}\n")
        
        print(f"{YELLOW}Dicas:{RESET}")
        print("  • Atualize o pip: python -m pip install --upgrade pip")
        print("  • Instale dependências: pip install -r requirements-minimal.txt")
        print("  • Configure .env: copy .env.example .env")
        print("  • Consulte: INSTALL.md\n")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_checks()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}⚠ Verificação interrompida pelo usuário{RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}✗ Erro fatal durante verificação: {e}{RESET}\n")
        sys.exit(1)