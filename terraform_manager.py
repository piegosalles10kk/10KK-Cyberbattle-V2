import subprocess
import json
import os
import time
from pathlib import Path

class TerraformManager:
    """Gerenciador de infraestrutura com Terraform"""
    
    def __init__(self, provider, os_template, vm_config, streamer):
        self.provider = provider
        self.os_template = os_template
        self.vm_config = vm_config
        self.streamer = streamer
        
        # Determinar diretório do Terraform baseado no provider e template
        self.terraform_dir = self._get_terraform_directory()
        
        # Validar diretório
        if not os.path.exists(self.terraform_dir):
            raise FileNotFoundError(f"Diretório Terraform não encontrado: {self.terraform_dir}")
        
        self.streamer.emit_log("INFO", f"Terraform configurado: {self.terraform_dir}")
    
    def _get_terraform_directory(self):
        """Determina o diretório Terraform baseado no provider e OS template"""
        # Estrutura esperada: ./iac/{provider}/{os_template}/
        base_dir = Path("./iac")
        terraform_dir = base_dir / self.provider / self.os_template
        
        # Fallback para estrutura antiga
        if not terraform_dir.exists():
            terraform_dir = Path("./infra_cyberduel")
        
        return str(terraform_dir)
    
    def reset_environment(self):
        """Executa destroy seguido de apply para resetar o ambiente"""
        self.streamer.emit_log("INFO", "🗑️ Iniciando Terraform Destroy...")
        self.destroy_environment()
        
        time.sleep(5)  # Pausa entre destroy e apply
        
        self.streamer.emit_log("INFO", "🚀 Iniciando Terraform Apply...")
        self.apply_environment()
    
    def destroy_environment(self):
        """Executa terraform destroy"""
        try:
            start_time = time.time()
            
            result = subprocess.run(
                ["terraform", "destroy", "-auto-approve"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                self.streamer.emit_log("SUCCESS", f"✅ Destroy concluído em {duration:.2f}s")
            else:
                self.streamer.emit_log("WARNING", f"⚠️ Destroy com avisos (código {result.returncode})")
                if result.stderr:
                    self.streamer.emit_log("DEBUG", f"Stderr: {result.stderr[:500]}")
        
        except subprocess.TimeoutExpired:
            self.streamer.emit_log("ERROR", "❌ Destroy excedeu timeout de 300s")
        except Exception as e:
            self.streamer.emit_log("WARNING", f"⚠️ Erro no destroy: {str(e)}")
    
    def apply_environment(self):
        """Executa terraform apply com variáveis do vm_config"""
        try:
            start_time = time.time()
            
            # Construir variáveis do Terraform a partir do vm_config
            tf_vars = self._build_terraform_vars()
            
            # Montar comando com variáveis
            cmd = ["terraform", "apply", "-auto-approve"]
            for var_name, var_value in tf_vars.items():
                cmd.extend(["-var", f"{var_name}={var_value}"])
            
            self.streamer.emit_log("DEBUG", f"Comando Terraform: {' '.join(cmd[:10])}...")
            
            result = subprocess.run(
                cmd,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            duration = time.time() - start_time
            
            if result.returncode != 0:
                self.streamer.emit_log("ERROR", f"❌ Apply falhou (código {result.returncode})")
                self.streamer.emit_log("ERROR", f"Stderr: {result.stderr[:1000]}")
                raise subprocess.CalledProcessError(result.returncode, cmd)
            
            self.streamer.emit_log("SUCCESS", f"✅ Apply concluído em {duration:.2f}s")
            
        except subprocess.TimeoutExpired:
            self.streamer.emit_log("ERROR", "❌ Apply excedeu timeout de 600s")
            raise
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro crítico no apply: {str(e)}")
            raise
    
    def _build_terraform_vars(self):
        """Converte vm_config em variáveis do Terraform"""
        return {
            "vm_cpu": self.vm_config.get('vm_cpu', 2),
            "vm_ram": self.vm_config.get('vm_ram_mb', 4096),
            "vm_switch": self.vm_config.get('vm_switch_name', 'Default Switch'),
            "base_vhdx_path": self.vm_config.get('base_vhdx_path', 'C:\\HyperV-Disks\\VM-BASE.vhdx'),
            "admin_user": self.vm_config.get('admin_user', 'adm'),
            "admin_password": self.vm_config.get('admin_password', 'adm123')
        }
    
    def get_vm_ips(self):
        """Captura os IPs das VMs do output do Terraform"""
        try:
            self.streamer.emit_log("INFO", "🔍 Capturando IPs do Terraform Output...")
            
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            outputs = json.loads(result.stdout)
            
            # Extrair IPs
            ips = {}
            for key, value in outputs.items():
                if 'ip_competidor' in key:
                    ip_value = value.get('value')
                    ips[key] = ip_value
                    self.streamer.emit_log("DEBUG", f"Capturado {key}: {ip_value}")
            
            if not ips:
                raise ValueError("Nenhum IP encontrado nos outputs do Terraform")
            
            return ips
            
        except subprocess.CalledProcessError as e:
            self.streamer.emit_log("ERROR", f"❌ Erro ao capturar outputs: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            self.streamer.emit_log("ERROR", f"❌ Erro ao parsear JSON do output: {str(e)}")
            raise
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro ao capturar IPs: {str(e)}")
            raise
    
    def init_terraform(self):
        """Executa terraform init (útil para primeiro uso)"""
        try:
            self.streamer.emit_log("INFO", "🔧 Executando Terraform Init...")
            
            result = subprocess.run(
                ["terraform", "init"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.streamer.emit_log("SUCCESS", "✅ Terraform Init concluído")
            else:
                self.streamer.emit_log("ERROR", f"❌ Init falhou: {result.stderr}")
                
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro no init: {str(e)}")
    
    def validate_terraform(self):
        """Valida a configuração do Terraform"""
        try:
            result = subprocess.run(
                ["terraform", "validate"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.streamer.emit_log("SUCCESS", "✅ Configuração Terraform válida")
                return True
            else:
                self.streamer.emit_log("ERROR", f"❌ Validação falhou: {result.stderr}")
                return False
                
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro na validação: {str(e)}")
            return False