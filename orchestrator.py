import time
import random
import base64
from datetime import datetime
from terraform_manager import TerraformManager
from attack_executor import AttackExecutor
from attack_database import AttackDatabase

class CyberDuelOrchestrator:
    """
    Orquestrador principal do CyberDuel - Versão API
    Gerencia todo o ciclo de vida do teste: setup, ataque, monitoramento e scoring
    """
    
    def __init__(self, payload, log_streamer):
        self.payload = payload
        self.streamer = log_streamer
        
        # Extrair configurações
        self.test_id = payload['test_id']
        self.test_name = payload['test_name']
        self.cloud_provider = payload['cloud_provider']
        self.os_template = payload['os_template']
        self.vm_config = payload['vm_config']
        self.edr_config = payload.get('edr_config', {})
        self.attack_config = payload.get('attack_config', {})
        
        # Componentes
        self.terraform_mgr = TerraformManager(
            provider=self.cloud_provider,
            os_template=self.os_template,
            vm_config=self.vm_config,
            streamer=self.streamer
        )
        
        self.attack_db = AttackDatabase()
        
        # Estado do teste
        self.vm_ips = {}
        self.test_results = {
            'test_id': self.test_id,
            'test_name': self.test_name,
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'infrastructure': {},
            'attacks': [],
            'final_score': {},
            'winner': None
        }
    
    def execute_full_test(self):
        """Executa o ciclo completo do teste"""
        self.test_results['start_time'] = datetime.utcnow().isoformat()
        start_time = time.time()
        
        try:
            # FASE 1: Setup da Infraestrutura
            self._phase_infrastructure_setup()
            
            # FASE 2: Instalação do EDR (se configurado)
            if self.edr_config:
                self._phase_edr_installation()
            
            # FASE 3: Execução dos Ataques
            self._phase_attack_execution()
            
            # FASE 4: Análise e Scoring
            self._phase_scoring_analysis()
            
            # FASE 5: Cleanup (opcional)
            # self._phase_cleanup()
            
        except Exception as e:
            self.streamer.emit_log("ERROR", f"Erro durante execução: {str(e)}")
            raise
        finally:
            end_time = time.time()
            self.test_results['end_time'] = datetime.utcnow().isoformat()
            self.test_results['duration_seconds'] = round(end_time - start_time, 2)
        
        return self.test_results
    
    def _phase_infrastructure_setup(self):
        """FASE 1: Setup da infraestrutura com Terraform"""
        self.streamer.emit_log("INFO", "📦 FASE 1: Setup da Infraestrutura", {
            "provider": self.cloud_provider,
            "os_template": self.os_template
        })
        
        # Destroy + Apply
        self.terraform_mgr.reset_environment()
        
        # Capturar IPs das VMs criadas
        self.vm_ips = self.terraform_mgr.get_vm_ips()
        
        self.test_results['infrastructure'] = {
            'provider': self.cloud_provider,
            'os_template': self.os_template,
            'vm_alpha': {
                'name': 'Host-A-Alpha',
                'ip': self.vm_ips.get('ip_competidor_a', 'N/A')
            },
            'vm_beta': {
                'name': 'Host-B-Beta',
                'ip': self.vm_ips.get('ip_competidor_b', 'N/A')
            }
        }
        
        self.streamer.emit_log("SUCCESS", "✅ Infraestrutura provisionada", self.vm_ips)
    
    def _phase_edr_installation(self):
        """FASE 2: Instalação do EDR nas VMs"""
        self.streamer.emit_log("INFO", "🛡️ FASE 2: Instalação do EDR", {
            "vendor": self.edr_config.get('vendor_name', 'N/A')
        })
        
        # Decodificar script de instalação
        installation_script = None
        if 'installation_script_base64' in self.edr_config:
            try:
                installation_script = base64.b64decode(
                    self.edr_config['installation_script_base64']
                ).decode('utf-8')
            except Exception as e:
                self.streamer.emit_log("WARNING", f"Erro ao decodificar script: {e}")
        
        if installation_script:
            # Instalar EDR nas duas VMs
            for vm_key, vm_ip in self.vm_ips.items():
                self.streamer.emit_log("INFO", f"Instalando EDR em {vm_key} ({vm_ip})")
                
                executor = AttackExecutor(
                    target_ip=vm_ip,
                    credentials={
                        'username': self.vm_config['admin_user'],
                        'password': self.vm_config['admin_password']
                    },
                    streamer=self.streamer
                )
                
                success = executor.execute_remote_script(installation_script)
                
                if success:
                    self.streamer.emit_log("SUCCESS", f"✅ EDR instalado em {vm_key}")
                else:
                    self.streamer.emit_log("WARNING", f"⚠️ Falha na instalação do EDR em {vm_key}")
        else:
            self.streamer.emit_log("INFO", "⏭️ Nenhum script de EDR fornecido, pulando instalação")
    
    def _phase_attack_execution(self):
        """FASE 3: Execução dos ataques"""
        self.streamer.emit_log("INFO", "⚔️ FASE 3: Execução dos Ataques")
        
        # Determinar qual ataque usar
        ttp_id = self.attack_config.get('ttp_id')
        attack_info = None
        
        if ttp_id:
            # Ataque específico do payload
            attack_info = self.attack_db.get_attack(ttp_id)
            if not attack_info:
                self.streamer.emit_log("WARNING", f"TTP {ttp_id} não encontrado no banco de dados")
                return
        else:
            # Se não especificado, usar ataques padrão
            self.streamer.emit_log("INFO", "Nenhum TTP específico, usando sequência padrão")
            attack_info = self._get_default_attack_sequence()
        
        # Executar ataques em ambas as VMs simultaneamente
        self._execute_simultaneous_attacks(attack_info)
    
    def _get_default_attack_sequence(self):
        """Retorna sequência padrão de 5 ataques"""
        default_ttps = [
            "T1059.001",  # PowerShell
            "T1027",      # Obfuscation
            "T1021.006",  # WinRM Lateral Move
            "T1070.001",  # Clear Logs
            "T1047"       # WMI
        ]
        return [self.attack_db.get_attack(ttp) for ttp in default_ttps]
    
    def _execute_simultaneous_attacks(self, attacks):
        """Executa ataques simultaneamente em ambas as VMs"""
        if not isinstance(attacks, list):
            attacks = [attacks]
        
        ip_alpha = self.vm_ips.get('ip_competidor_a')
        ip_beta = self.vm_ips.get('ip_competidor_b')
        
        if not ip_alpha or not ip_beta:
            self.streamer.emit_log("ERROR", "IPs das VMs não disponíveis")
            return
        
        # Criar executores
        executor_alpha = AttackExecutor(
            target_ip=ip_alpha,
            credentials={
                'username': self.vm_config['admin_user'],
                'password': self.vm_config['admin_password']
            },
            streamer=self.streamer
        )
        
        executor_beta = AttackExecutor(
            target_ip=ip_beta,
            credentials={
                'username': self.vm_config['admin_user'],
                'password': self.vm_config['admin_password']
            },
            streamer=self.streamer
        )
        
        # Executar cada ataque
        for attack in attacks:
            if not attack:
                continue
            
            self.streamer.emit_log("INFO", f"🎯 Executando {attack['ttp_id']} - {attack['ttp_name']}")
            
            # Selecionar payload (usar 'basic' por padrão)
            payload_script = attack['payloads'].get('basic', list(attack['payloads'].values())[0])
            
            # Executar em Alpha
            result_alpha = self._execute_attack_on_vm(
                executor_alpha,
                "Alpha",
                attack,
                payload_script
            )
            
            # Executar em Beta
            result_beta = self._execute_attack_on_vm(
                executor_beta,
                "Beta",
                attack,
                payload_script
            )
            
            # Armazenar resultados
            self.test_results['attacks'].append({
                'ttp_id': attack['ttp_id'],
                'ttp_name': attack['ttp_name'],
                'alpha_result': result_alpha,
                'beta_result': result_beta
            })
            
            # Pequena pausa entre ataques
            time.sleep(2)
    
    def _execute_attack_on_vm(self, executor, vm_name, attack, payload_script):
        """Executa um ataque específico em uma VM e monitora"""
        start_time = time.time()
        
        # 1. Executar o ataque
        success = executor.execute_remote_script(payload_script)
        execution_time = time.time() - start_time
        
        # 2. Simular detecção e resposta do EDR
        detection_result = self._simulate_edr_detection(attack, execution_time)
        
        # 3. Calcular pontuação
        score = self._calculate_defense_score(detection_result, attack)
        
        result = {
            'vm': vm_name,
            'attack_executed': success,
            'execution_time': round(execution_time, 2),
            'edr_detected': detection_result['detected'],
            'edr_blocked': detection_result['blocked'],
            'edr_response_time': detection_result['response_time'],
            'damage_dealt': detection_result['damage'],
            'defense_points': score
        }
        
        # Log do resultado
        status_emoji = "✅" if detection_result['blocked'] else "❌"
        self.streamer.emit_log("INFO", 
            f"{status_emoji} {vm_name}: {'BLOQUEADO' if detection_result['blocked'] else 'NÃO BLOQUEADO'} "
            f"| Dano: {detection_result['damage']} HP | Pontos: +{score}",
            result
        )
        
        return result
    
    def _simulate_edr_detection(self, attack, execution_time):
        """Simula detecção e resposta do EDR (baseado em probabilidades)"""
        # Taxas de detecção baseadas na severidade
        detection_rates = {
            'LOW': 0.70,
            'MEDIUM': 0.85,
            'HIGH': 0.95,
            'CRITICAL': 0.98
        }
        
        blocking_rates = {
            'LOW': 0.50,
            'MEDIUM': 0.65,
            'HIGH': 0.80,
            'CRITICAL': 0.90
        }
        
        severity = attack.get('severity', 'MEDIUM')
        
        # Simular detecção
        detected = random.random() < detection_rates.get(severity, 0.85)
        
        # Simular bloqueio (só pode bloquear se detectou)
        blocked = detected and (random.random() < blocking_rates.get(severity, 0.65))
        
        # Tempo de resposta do EDR (simulado)
        response_time = random.uniform(0.1, 3.0)
        
        # Calcular dano
        damage = 0 if blocked else attack.get('expected_damage', 20)
        
        return {
            'detected': detected,
            'blocked': blocked,
            'response_time': round(response_time, 2),
            'damage': damage
        }
    
    def _calculate_defense_score(self, detection_result, attack):
        """Calcula pontos de defesa baseado na resposta do EDR"""
        score = 0
        
        # +10 pontos por detecção
        if detection_result['detected']:
            score += 10
        
        # +20 pontos por bloqueio
        if detection_result['blocked']:
            score += 20
        
        # +5 pontos por resposta rápida (< 1 segundo)
        if detection_result['response_time'] < 1.0 and detection_result['detected']:
            score += 5
        
        # Bônus por severidade do ataque bloqueado
        if detection_result['blocked']:
            severity_bonus = {
                'LOW': 5,
                'MEDIUM': 10,
                'HIGH': 15,
                'CRITICAL': 20
            }
            score += severity_bonus.get(attack.get('severity', 'MEDIUM'), 10)
        
        return score
    
    def _phase_scoring_analysis(self):
        """FASE 4: Análise final e determinação do vencedor"""
        self.streamer.emit_log("INFO", "📊 FASE 4: Análise e Scoring Final")
        
        # Agregar resultados
        alpha_damage = 0
        alpha_defense = 0
        beta_damage = 0
        beta_defense = 0
        
        for attack_result in self.test_results['attacks']:
            alpha_res = attack_result.get('alpha_result', {})
            beta_res = attack_result.get('beta_result', {})
            
            alpha_damage += alpha_res.get('damage_dealt', 0)
            alpha_defense += alpha_res.get('defense_points', 0)
            
            beta_damage += beta_res.get('damage_dealt', 0)
            beta_defense += beta_res.get('defense_points', 0)
        
        # Calcular HP final (assumindo MAX_HP = 100)
        alpha_hp = max(0, 100 - alpha_damage)
        beta_hp = max(0, 100 - beta_damage)
        
        self.test_results['final_score'] = {
            'alpha': {
                'hp_remaining': alpha_hp,
                'damage_taken': alpha_damage,
                'defense_points': alpha_defense,
                'total_score': alpha_hp + alpha_defense
            },
            'beta': {
                'hp_remaining': beta_hp,
                'damage_taken': beta_damage,
                'defense_points': beta_defense,
                'total_score': beta_hp + beta_defense
            }
        }
        
        # Determinar vencedor
        if alpha_hp > beta_hp:
            winner = "Alpha"
        elif beta_hp > alpha_hp:
            winner = "Beta"
        else:
            # Empate em HP, desempatar por pontos de defesa
            if alpha_defense > beta_defense:
                winner = "Alpha (Desempate por Pontos)"
            elif beta_defense > alpha_defense:
                winner = "Beta (Desempate por Pontos)"
            else:
                winner = "Empate Técnico"
        
        self.test_results['winner'] = winner
        
        self.streamer.emit_log("SUCCESS", f"🏆 VENCEDOR: {winner}", self.test_results['final_score'])
    
    def _phase_cleanup(self):
        """FASE 5: Limpeza da infraestrutura (opcional)"""
        self.streamer.emit_log("INFO", "🧹 FASE 5: Limpeza da Infraestrutura")
        self.terraform_mgr.destroy_environment()
        self.streamer.emit_log("SUCCESS", "✅ Infraestrutura destruída")