# infra_cyberduel/modules/competitor_vm/main.tf

# --- Configuração do Provedor ---
terraform {
  required_providers {
    hyperv = {
      source  = "taliesins/hyperv"
      version = ">= 1.0.3"
    }
    null = { 
      source  = "hashicorp/null"
      version = "~> 3.2"
    }
    // ADICIONADO: Provedor time para criar o atraso (sleep)
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9.1"
    }
  }
}

# --- Variáveis do Módulo ---
variable "vm_name" {}
# ALTERAÇÃO: TORNADA OPCIONAL PARA PERMITIR DHCP
variable "vm_ip" { 
  default = null
} 
variable "vm_cpu" { 
  default = 1 
}
variable "vm_ram" {} # Em MB
variable "vm_switch_name" {}
variable "vm_base_vhdxpath" {} 
variable "admin_user" {}
variable "admin_password" {} 

# --- Locals e VHD ---
locals {
  vm_path      = "C:\\HyperV\\VMs\\${var.vm_name}"
  new_vhd_path = "${local.vm_path}\\disk.vhdx"
}

resource "hyperv_vhd" "competitor_vhd" {
  path        = local.new_vhd_path 
  parent_path = var.vm_base_vhdxpath 
  vhd_type    = "Differencing"
}


# 2. Criar VM Hyper-V (RECURSO hyperv_machine_instance)
resource "hyperv_machine_instance" "competitor_host" {
  
  name = var.vm_name
  generation            = 2
  processor_count       = var.vm_cpu 
  memory_startup_bytes  = var.vm_ram * 1024 * 1024 
  static_memory         = true 
  state = "Running"

  # ✅ PROPRIEDADES DE TIMEOUT DA MÁQUINA
  wait_for_state_timeout   = 60 
  wait_for_ips_timeout     = 600 # Tempo máximo para encontrar um IP dinâmico
  wait_for_ips_poll_period = 10 

  # --- ANEXAR O DISCO PRINCIPAL ---
  hard_disk_drives {
    controller_type   = "Scsi"
    controller_number = 0
    controller_location = 0 
    path              = hyperv_vhd.competitor_vhd.path 
  }
  
  # --- CONFIGURAÇÃO DE REDE (DHCP para inicialização, wait_for_ips = True) ---
  network_adaptors {
    name          = "Network Adapter"
    switch_name   = var.vm_switch_name
    wait_for_ips  = true 
  }
  
  # --- ANEXAR DRIVE DE DVD ---
  dvd_drives {
    controller_number   = 0
    controller_location = 1
  }
}


// ======================================================================================
// 1. SOLUÇÃO DE ENCODING: Ativa os Serviços de Integração (Host-side)
// ======================================================================================

resource "null_resource" "enable_integration_services" {
  depends_on = [hyperv_machine_instance.competitor_host]

  triggers = {
    vm_name = var.vm_name
  }

  provisioner "local-exec" {
    command = <<-EOT
      Import-Module Hyper-V -ErrorAction Stop
      $OutputEncoding = [System.Text.Encoding]::UTF8

      $ServiceName = @(
        "Interface de Serviço de Convidado",
        "Pulsação",
        "Troca do Par Chave-Valor",
        "Desligamento",
        "Sincronização de Data/Hora",
        "VSS"
      )
      
      foreach ($Service in $ServiceName) {
          Write-Host "Tentando habilitar o serviço de integração: '$Service' na VM '${var.vm_name}'"
          try {
              Get-VMIntegrationService -VMName "${var.vm_name}" | Where-Object { $_.Name -eq $Service } | Enable-VMIntegrationService -ErrorAction Stop
              Write-Host "Serviço '$Service' habilitado com sucesso."
          }
          catch {
              Write-Host "ERRO ao habilitar '$Service': $($_.Exception.Message)"
          }
      }
    EOT
    interpreter = ["powershell", "-ExecutionPolicy", "Bypass", "-Command"]
  }
}

// ======================================================================================
// 1B. DELAY (NOVO RECURSO): Espera obrigatória para o Windows iniciar e reportar o IP
// ======================================================================================

resource "time_sleep" "wait_for_guest_ip" {
  // Espera após a ativação dos Integration Services
  depends_on = [
    null_resource.enable_integration_services
  ]
  
  // Atraso de 90 segundos para dar tempo ao Windows de iniciar e obter DHCP
  create_duration = "90s" 
}

# ADICIONAR ISTO ANTES DO OUTPUT
resource "null_resource" "wait_for_ip_active" {
  depends_on = [time_sleep.wait_for_guest_ip]
  
  provisioner "local-exec" {
    command = <<-EOT
      $maxAttempts = 20
      $attempt = 0
      
      Write-Host "Aguardando IP para VM ${var.vm_name}..."
      
      do {
        $attempt++
        Write-Host "Tentativa $attempt/$maxAttempts..."
        
        $vm = Get-VM -Name "${var.vm_name}" -ErrorAction SilentlyContinue
        if ($vm) {
          $adapters = Get-VMNetworkAdapter -VMName "${var.vm_name}" -ErrorAction SilentlyContinue
          if ($adapters) {
            $ip = $adapters.IPAddresses | Where-Object {$_ -match '^\d+\.\d+\.\d+\.\d+$'} | Select-Object -First 1
            
            if ($ip) {
              Write-Host "✓ IP detectado: $ip"
              exit 0
            }
          }
        }
        
        if ($attempt -lt $maxAttempts) {
          Write-Host "IP ainda não detectado. Aguardando 10 segundos..."
          Start-Sleep -Seconds 10
        }
      } while ($attempt -lt $maxAttempts)
      
      Write-Host "AVISO: IP não detectado após $maxAttempts tentativas, mas continuando..."
      exit 0
    EOT
    interpreter = ["powershell", "-ExecutionPolicy", "Bypass", "-Command"]
  }
}

# Output modificado para depender do wait
output "real_ip_address" {
  depends_on = [null_resource.wait_for_ip_active]
  
  value = (
    length(hyperv_machine_instance.competitor_host.network_adaptors) > 0 &&
    length(hyperv_machine_instance.competitor_host.network_adaptors[0].ip_addresses) > 0
  ) ? hyperv_machine_instance.competitor_host.network_adaptors[0].ip_addresses[0] : "IP_NOT_READY"
  
  description = "O endereço IP real (dinâmico via DHCP) detectado pelo Hyper-V provider."
}