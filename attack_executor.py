import winrm
import time
from datetime import datetime

class AttackExecutor:
    """Executa ataques remotos via WinRM"""
    
    def __init__(self, target_ip, credentials, streamer):
        self.target_ip = target_ip
        self.username = credentials['username']
        self.password = credentials['password']
        self.streamer = streamer
        
        # Configuração WinRM
        self.winrm_port = 5985
        self.winrm_transport = 'ntlm'
        self.max_retries = 3
        self.retry_delay = 5
    
    def test_connection(self):
        """Testa conectividade WinRM com o host"""
        try:
            session = self._create_session()
            result = session.run_cmd('echo Connection Test')
            
            if result.status_code == 0:
                self.streamer.emit_log("SUCCESS", f"✅ Conexão WinRM estabelecida com {self.target_ip}")
                return True
            else:
                self.streamer.emit_log("ERROR", f"❌ Teste de conexão falhou para {self.target_ip}")
                return False
                
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro ao testar conexão: {str(e)}")
            return False
    
    def execute_remote_script(self, script_content, retry=True):
        """
        Executa script PowerShell/CMD remotamente via WinRM
        
        Args:
            script_content: String contendo o script a ser executado
            retry: Se True, tenta novamente em caso de falha
            
        Returns:
            bool: True se executado com sucesso, False caso contrário
        """
        attempts = self.max_retries if retry else 1
        
        for attempt in range(1, attempts + 1):
            try:
                self.streamer.emit_log("DEBUG", 
                    f"Executando script em {self.target_ip} (Tentativa {attempt}/{attempts})"
                )
                
                session = self._create_session()
                start_time = time.time()
                
                # Executar script
                result = session.run_cmd(script_content)
                execution_time = time.time() - start_time
                
                # Processar resultado
                if result.status_code == 0:
                    stdout = result.std_out.decode('utf-8', errors='ignore').strip()
                    
                    self.streamer.emit_log("SUCCESS", 
                        f"✅ Script executado com sucesso em {execution_time:.2f}s",
                        {
                            "target": self.target_ip,
                            "execution_time": round(execution_time, 2),
                            "output_preview": stdout[:200] if stdout else "Sem output"
                        }
                    )
                    return True
                else:
                    stderr = result.std_err.decode('utf-8', errors='ignore').strip()
                    self.streamer.emit_log("WARNING", 
                        f"⚠️ Script retornou código {result.status_code}",
                        {
                            "target": self.target_ip,
                            "status_code": result.status_code,
                            "error": stderr[:200] if stderr else "Sem erro específico"
                        }
                    )
                    
                    if attempt < attempts:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                    
            except winrm.exceptions.WinRMTransportError as e:
                self.streamer.emit_log("ERROR", 
                    f"❌ Erro de transporte WinRM (Tentativa {attempt}): {str(e)}"
                )
                if attempt < attempts:
                    time.sleep(self.retry_delay)
                    continue
                return False
                
            except winrm.exceptions.InvalidCredentialsError:
                self.streamer.emit_log("ERROR", 
                    f"❌ Credenciais inválidas para {self.target_ip}"
                )
                return False  # Não retentar com credenciais inválidas
                
            except Exception as e:
                self.streamer.emit_log("ERROR", 
                    f"❌ Erro ao executar script (Tentativa {attempt}): {str(e)}"
                )
                if attempt < attempts:
                    time.sleep(self.retry_delay)
                    continue
                return False
        
        return False
    
    def execute_validation_check(self, validation_command):
        """
        Executa comando de validação pós-ataque
        
        Args:
            validation_command: Comando PowerShell para validar artefatos do ataque
            
        Returns:
            dict: Resultado da validação
        """
        try:
            self.streamer.emit_log("INFO", f"🔍 Executando validação em {self.target_ip}")
            
            session = self._create_session()
            result = session.run_cmd(validation_command)
            
            stdout = result.std_out.decode('utf-8', errors='ignore').strip()
            stderr = result.std_err.decode('utf-8', errors='ignore').strip()
            
            validation_result = {
                "target": self.target_ip,
                "success": result.status_code == 0,
                "status_code": result.status_code,
                "output": stdout,
                "error": stderr,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if result.status_code == 0:
                self.streamer.emit_log("SUCCESS", "✅ Validação bem-sucedida", validation_result)
            else:
                self.streamer.emit_log("WARNING", "⚠️ Validação falhou", validation_result)
            
            return validation_result
            
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro na validação: {str(e)}")
            return {
                "target": self.target_ip,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def upload_file(self, local_path, remote_path):
        """
        Faz upload de arquivo para o host remoto (via PowerShell)
        
        Args:
            local_path: Caminho do arquivo local
            remote_path: Caminho de destino no host remoto
            
        Returns:
            bool: True se upload bem-sucedido
        """
        try:
            import base64
            
            # Ler arquivo local
            with open(local_path, 'rb') as f:
                file_content = f.read()
            
            # Encodar em Base64
            encoded_content = base64.b64encode(file_content).decode('utf-8')
            
            # Script PowerShell para decodificar e salvar
            upload_script = f"""
            $base64 = '{encoded_content}'
            $bytes = [System.Convert]::FromBase64String($base64)
            [System.IO.File]::WriteAllBytes('{remote_path}', $bytes)
            Write-Host 'File uploaded successfully'
            """
            
            self.streamer.emit_log("INFO", f"📤 Fazendo upload de {local_path} para {remote_path}")
            
            return self.execute_remote_script(upload_script, retry=False)
            
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro no upload: {str(e)}")
            return False
    
    def download_file(self, remote_path, local_path):
        """
        Faz download de arquivo do host remoto
        
        Args:
            remote_path: Caminho do arquivo no host remoto
            local_path: Caminho de destino local
            
        Returns:
            bool: True se download bem-sucedido
        """
        try:
            import base64
            
            # Script PowerShell para ler e encodar arquivo
            download_script = f"""
            $bytes = [System.IO.File]::ReadAllBytes('{remote_path}')
            $base64 = [System.Convert]::ToBase64String($bytes)
            Write-Host $base64
            """
            
            session = self._create_session()
            result = session.run_cmd(download_script)
            
            if result.status_code == 0:
                # Decodificar Base64
                encoded_content = result.std_out.decode('utf-8').strip()
                file_content = base64.b64decode(encoded_content)
                
                # Salvar localmente
                with open(local_path, 'wb') as f:
                    f.write(file_content)
                
                self.streamer.emit_log("SUCCESS", f"✅ Download de {remote_path} concluído")
                return True
            else:
                self.streamer.emit_log("ERROR", f"❌ Falha no download de {remote_path}")
                return False
                
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro no download: {str(e)}")
            return False
    
    def get_system_info(self):
        """Coleta informações do sistema remoto"""
        try:
            info_script = """
            $info = @{
                Hostname = $env:COMPUTERNAME
                OS = (Get-CimInstance Win32_OperatingSystem).Caption
                OSVersion = (Get-CimInstance Win32_OperatingSystem).Version
                Architecture = $env:PROCESSOR_ARCHITECTURE
                RAM = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
                CPU = (Get-CimInstance Win32_Processor).Name
                IPAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -ne '127.0.0.1'} | Select-Object -First 1).IPAddress
            }
            $info | ConvertTo-Json
            """
            
            session = self._create_session()
            result = session.run_cmd(info_script)
            
            if result.status_code == 0:
                import json
                info = json.loads(result.std_out.decode('utf-8'))
                self.streamer.emit_log("INFO", "ℹ️ Informações do sistema coletadas", info)
                return info
            else:
                return None
                
        except Exception as e:
            self.streamer.emit_log("ERROR", f"❌ Erro ao coletar info do sistema: {str(e)}")
            return None
    
    def _create_session(self):
        """Cria sessão WinRM"""
        return winrm.Session(
            self.target_ip,
            auth=(self.username, self.password),
            transport=self.winrm_transport,
            server_cert_validation='ignore'
        )