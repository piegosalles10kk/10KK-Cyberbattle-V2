"""
Configurações centralizadas da CyberDuel API
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configuração base"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # API
    API_VERSION = 'v1'
    API_TITLE = 'CyberDuel API'
    API_DESCRIPTION = 'API para testes automatizados de EDR usando MITRE ATT&CK'
    
    # Servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    THREADED = True
    
    # CORS
    CORS_ENABLED = os.getenv('CORS_ENABLED', 'True').lower() == 'true'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Terraform
    TERRAFORM_BASE_DIR = Path(os.getenv('TERRAFORM_BASE_DIR', './iac'))
    TERRAFORM_TIMEOUT_DESTROY = int(os.getenv('TERRAFORM_TIMEOUT_DESTROY', 300))
    TERRAFORM_TIMEOUT_APPLY = int(os.getenv('TERRAFORM_TIMEOUT_APPLY', 600))
    TERRAFORM_TIMEOUT_OUTPUT = int(os.getenv('TERRAFORM_TIMEOUT_OUTPUT', 30))
    
    # WinRM
    WINRM_PORT = int(os.getenv('WINRM_PORT', 5985))
    WINRM_TRANSPORT = os.getenv('WINRM_TRANSPORT', 'ntlm')
    WINRM_MAX_RETRIES = int(os.getenv('WINRM_MAX_RETRIES', 3))
    WINRM_RETRY_DELAY = int(os.getenv('WINRM_RETRY_DELAY', 5))
    WINRM_TIMEOUT = int(os.getenv('WINRM_TIMEOUT', 300))
    
    # Teste
    TEST_MAX_DURATION = int(os.getenv('TEST_MAX_DURATION', 3600))  # 1 hora
    TEST_MAX_CONCURRENT = int(os.getenv('TEST_MAX_CONCURRENT', 5))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'cyberduel.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Segurança
    ALLOWED_CLOUD_PROVIDERS = ['hyperv', 'azure', 'aws', 'gcp']
    ALLOWED_OS_TEMPLATES = [
        'windows-server-2022-base',
        'windows-server-2019-base',
        'windows-11-pro',
        'windows-10-pro',
        'windows-10-enterprise'
    ]
    
    # Limites de VM
    VM_CPU_MIN = 1
    VM_CPU_MAX = 16
    VM_RAM_MIN = 1024  # MB
    VM_RAM_MAX = 32768  # MB
    
    # Diretórios
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / 'logs'
    TEMP_DIR = BASE_DIR / 'temp'
    RESULTS_DIR = BASE_DIR / 'results'
    
    @classmethod
    def init_directories(cls):
        """Cria diretórios necessários se não existirem"""
        for directory in [cls.LOGS_DIR, cls.TEMP_DIR, cls.RESULTS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Valida configurações críticas"""
        errors = []
        
        if not cls.TERRAFORM_BASE_DIR.exists():
            errors.append(f"Diretório Terraform não encontrado: {cls.TERRAFORM_BASE_DIR}")
        
        if cls.VM_CPU_MAX < cls.VM_CPU_MIN:
            errors.append("VM_CPU_MAX deve ser maior que VM_CPU_MIN")
        
        if cls.VM_RAM_MAX < cls.VM_RAM_MIN:
            errors.append("VM_RAM_MAX deve ser maior que VM_RAM_MIN")
        
        return errors


class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    TESTING = False
    
    # Em produção, exigir variáveis de ambiente
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY deve ser definida em produção")
    
    # Desabilitar CORS aberto em produção
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    if '*' in CORS_ORIGINS:
        raise ValueError("CORS não deve permitir * em produção")


class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    DEBUG = True
    
    # Usar diretórios temporários para testes
    TERRAFORM_BASE_DIR = Path('./tests/fixtures/iac')
    LOGS_DIR = Path('./tests/temp/logs')
    TEMP_DIR = Path('./tests/temp')
    RESULTS_DIR = Path('./tests/temp/results')
    
    # Timeouts curtos para testes
    TERRAFORM_TIMEOUT_DESTROY = 10
    TERRAFORM_TIMEOUT_APPLY = 10
    WINRM_TIMEOUT = 10
    TEST_MAX_DURATION = 60


# Mapeamento de configurações
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Retorna a configuração apropriada
    
    Args:
        config_name: Nome da configuração ('development', 'production', 'testing')
                    Se None, usa a variável de ambiente FLASK_ENV
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)