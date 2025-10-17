# infra_cyberduel/main.tf

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
  }
}

# Provider Hyper-V (Ajuste as credenciais conforme seu sistema)
provider "hyperv" {
  host            = "127.0.0.1"
  port            = 5985
  https           = false
  use_ntlm        = true
  user            = "10kk"  
  password        = "1234"
}

# --- VM COMPETIDOR A (Time Alpha) ---
module "vm_competidor_a" {
  source           = "./modules/competitor_vm"
  vm_name          = "Host-A-Alpha"
  vm_cpu           = var.vm_cpu
  vm_ram           = var.vm_ram
  vm_switch_name   = var.vm_switch
  vm_base_vhdxpath = var.base_vhdx_path
  admin_user       = var.admin_user
  admin_password   = var.admin_password
}

# --- VM COMPETIDOR B (Time Beta) ---
module "vm_competidor_b" {
  source           = "./modules/competitor_vm"
  vm_name          = "Host-B-Beta"
  vm_cpu           = var.vm_cpu
  vm_ram           = var.vm_ram
  vm_switch_name   = var.vm_switch
  vm_base_vhdxpath = var.base_vhdx_path
  admin_user       = var.admin_user
  admin_password   = var.admin_password
}

# Outputs (Retorna o IP estático definido)
output "ip_competidor_a" {
  value       = module.vm_competidor_a.real_ip_address
  description = "IP estático configurado para o Competidor A (Time Alpha)."
}

output "ip_competidor_b" {
  value       = module.vm_competidor_b.real_ip_address
  description = "IP estático configurado para o Competidor B (Time Beta)."
}