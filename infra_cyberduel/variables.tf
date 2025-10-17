# infra_cyberduel/variables.tf

# --- Configuração do Ambiente Hyper-V ---

variable "vm_cpu" {
  description = "Número de vCPUs para cada VM."
  default     = 2
}

variable "vm_ram" {
  description = "Quantidade de RAM em MB para cada VM (ex: 4096 para 4GB)."
  default     = 3096 
}

variable "vm_switch" {
  description = "Nome do switch virtual no Hyper-V que as VMs usarão (ex: Default Switch)."
  default     = "Default Switch" 
}

variable "base_vhdx_path" {
  description = "Caminho COMPLETO para o VHDX da sua VM base limpa (Windows 10)."
  default     = "C:\\HyperV-Disks\\VM-BASE.vhdx"
}


# --- Credenciais de Provisionamento (WinRM) ---

variable "admin_user" {
  description = "Usuário Administrador da VM para conexão WinRM (usado pelo Python)."
  default     = "adm" 
}

variable "admin_password" {
  description = "Senha do Usuário Administrador da VM."
  default     = "adm123"
}