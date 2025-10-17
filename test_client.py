"""
Cliente de teste para a CyberDuel API
Facilita testes e demonstrações da API
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Optional

class CyberDuelClient:
    """Cliente para interagir com a CyberDuel API"""
    
    def __init__(self, base_url: str = "http://localhost:5000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def health_check(self) -> Dict:
        """Verifica o status da API"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def list_attacks(self) -> Dict:
        """Lista todos os ataques disponíveis"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/attacks/list")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def get_attack(self, ttp_id: str) -> Dict:
        """Obtém detalhes de um ataque específico"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/attacks/{ttp_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def execute_test(self, payload: Dict, callback=None) -> Dict:
        """
        Executa um teste e processa logs em tempo real
        
        Args:
            payload: Payload do teste
            callback: Função callback(log_entry) para processar cada log
        
        Returns:
            Dict com o resultado final do teste
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/cyberduel/execute",
                json=payload,
                stream=True,
                timeout=3600  # 1 hora de timeout
            )
            response.raise_for_status()
            
            final_result = None
            
            # Processar stream de logs
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_str = line.decode('utf-8')
                
                # Server-Sent Events vem com prefixo "data: "
                if line_str.startswith('data: '):
                    data_json = line_str[6:]
                    
                    try:
                        log_entry = json.loads(data_json)
                        
                        # Verificar se é o evento de conclusão
                        if log_entry.get('status') == 'completed':
                            break
                        
                        # Chamar callback se fornecido
                        if callback:
                            callback(log_entry)
                        else:
                            self._default_log_handler(log_entry)
                        
                        # Salvar último log com dados completos
                        if 'data' in log_entry and log_entry['data']:
                            final_result = log_entry
                    
                    except json.JSONDecodeError as e:
                        print(f"Erro ao parsear JSON: {e}")
                        continue
            
            return final_result or {"status": "completed"}
        
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}
    
    def _default_log_handler(self, log_entry: Dict):
        """Handler padrão para logs"""
        timestamp = log_entry.get('timestamp', '')
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')
        
        # Emojis para níveis
        emoji_map = {
            'DEBUG': '🔍',
            'INFO': 'ℹ️',
            'SUCCESS': '✅',
            'WARNING': '⚠️',
            'ERROR': '❌'
        }
        emoji = emoji_map.get(level, '📝')
        
        # Colorir output (ANSI colors)
        color_map = {
            'DEBUG': '\033[90m',     # Cinza
            'INFO': '\033[94m',      # Azul
            'SUCCESS': '\033[92m',   # Verde
            'WARNING': '\033[93m',   # Amarelo
            'ERROR': '\033[91m'      # Vermelho
        }
        reset_color = '\033[0m'
        color = color_map.get(level, '')
        
        print(f"{color}{emoji} [{level}] {message}{reset_color}")
        
        # Imprimir dados adicionais se houver
        data = log_entry.get('data', {})
        if data and level in ['SUCCESS', 'ERROR']:
            print(f"   └─ Dados: {json.dumps(data, indent=6)}")


def print_banner():
    """Exibe banner da aplicação"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║       🛡️  CYBERDUEL API - TEST CLIENT  ⚔️                ║
    ║                                                           ║
    ║       Teste automatizado de EDR com MITRE ATT&CK         ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def example_basic_test():
    """Exemplo de teste básico"""
    payload = {
        "test_id": f"T-CLI-{int(time.time())}",
        "test_name": "Teste via Cliente Python",
        "cloud_provider": "hyperv",
        "os_template": "windows-server-2022-base",
        "vm_config": {
            "vm_cpu": 2,
            "vm_ram_mb": 3096,
            "vm_switch_name": "Default Switch",
            "base_vhdx_path": "C:\\HyperV-Disks\\VM-BASE.vhdx",
            "admin_user": "adm",
            "admin_password": "adm123"
        },
        "attack_config": {
            "ttp_id": "T1059.001"
        }
    }
    return payload


def main():
    """Função principal do cliente de teste"""
    print_banner()
    
    # Configurar cliente
    api_url = input("URL da API [http://localhost:5000]: ").strip() or "http://localhost:5000"
    client = CyberDuelClient(base_url=api_url)
    
    # Health check
    print("\n🔍 Verificando status da API...")
    health = client.health_check()
    if health.get('status') == 'healthy':
        print(f"✅ API está saudável! Timestamp: {health.get('timestamp')}")
    else:
        print(f"❌ API não está respondendo: {health}")
        return 1
    
    # Menu
    while True:
        print("\n" + "="*60)
        print("MENU PRINCIPAL")
        print("="*60)
        print("1. Listar todos os ataques disponíveis")
        print("2. Ver detalhes de um ataque específico")
        print("3. Executar teste básico (exemplo)")
        print("4. Executar teste customizado (JSON)")
        print("5. Executar teste de arquivo JSON")
        print("0. Sair")
        print("="*60)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            print("\n📋 Listando ataques...")
            attacks = client.list_attacks()
            if attacks.get('status') == 'success':
                print(f"\n✅ Total de {attacks['total']} ataques disponíveis:\n")
                for attack in attacks['attacks']:
                    print(f"  • {attack['ttp_id']}: {attack['ttp_name']}")
                    print(f"    Tática: {attack['tactic']} | Severidade: {attack['severity']}")
                    print(f"    {attack['description']}\n")
            else:
                print(f"❌ Erro: {attacks}")
        
        elif choice == '2':
            ttp_id = input("\nDigite o TTP ID (ex: T1059.001): ").strip()
            print(f"\n🔍 Buscando detalhes de {ttp_id}...")
            attack = client.get_attack(ttp_id)
            if attack.get('status') == 'success':
                details = attack['attack']
                print(f"\n✅ Detalhes de {details['ttp_id']}:")
                print(f"Nome: {details['ttp_name']}")
                print(f"Tática: {details['tactic']}")
                print(f"Severidade: {details['severity']}")
                print(f"Descrição: {details['description']}")
                print(f"Dano Esperado: {details['expected_damage']} HP")
                print(f"\nPayloads disponíveis:")
                for payload_name, payload_cmd in details['payloads'].items():
                    print(f"  • {payload_name}:")
                    print(f"    {payload_cmd[:100]}...")
            else:
                print(f"❌ Erro: {attack}")
        
        elif choice == '3':
            print("\n🚀 Executando teste básico...")
            print("\n⚠️  ATENÇÃO: Este teste irá:")
            print("   - Executar terraform destroy + apply")
            print("   - Criar 2 VMs no Hyper-V")
            print("   - Executar ataques simulados")
            print("   - Pode levar de 15 a 30 minutos\n")
            
            confirm = input("Deseja continuar? (s/N): ").strip().lower()
            if confirm != 's':
                print("❌ Teste cancelado.")
                continue
            
            payload = example_basic_test()
            print("\n" + "="*60)
            print("INICIANDO TESTE")
            print("="*60)
            start_time = time.time()
            
            result = client.execute_test(payload)
            
            duration = time.time() - start_time
            print("\n" + "="*60)
            print(f"TESTE CONCLUÍDO em {duration:.2f} segundos")
            print("="*60)
            
            if result:
                print("\n📊 RESULTADO FINAL:")
                print(json.dumps(result.get('data', {}), indent=2))
        
        elif choice == '4':
            print("\n📝 Cole o payload JSON (termine com uma linha vazia):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            
            try:
                payload = json.loads('\n'.join(lines))
                print("\n🚀 Executando teste customizado...")
                result = client.execute_test(payload)
                print("\n📊 Resultado:", json.dumps(result, indent=2))
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao parsear JSON: {e}")
        
        elif choice == '5':
            filepath = input("\nCaminho do arquivo JSON: ").strip()
            try:
                with open(filepath, 'r') as f:
                    payload = json.load(f)
                print(f"\n🚀 Executando teste de {filepath}...")
                result = client.execute_test(payload)
                print("\n📊 Resultado:", json.dumps(result, indent=2))
            except FileNotFoundError:
                print(f"❌ Arquivo não encontrado: {filepath}")
            except json.JSONDecodeError as e:
                print(f"❌ Erro ao parsear JSON: {e}")
        
        elif choice == '0':
            print("\n👋 Encerrando cliente...")
            break
        
        else:
            print("\n❌ Opção inválida!")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário. Encerrando...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)