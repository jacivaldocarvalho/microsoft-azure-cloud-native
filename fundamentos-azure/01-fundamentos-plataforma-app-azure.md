# 🟦 Fundamentos da Plataforma de Aplicações no Azure

## ☁️ Computação em Nuvem

### 🔹 O que é computação em nuvem?

Computação em nuvem é a entrega de serviços de TI sob demanda por meio da internet, com pagamento conforme o uso. Permite acessar recursos de computação, armazenamento, rede, entre outros, sem a necessidade de investir em infraestrutura local.


### 🔹 Modelos de Computação em Nuvem

#### • Nuvem Pública

Serviços oferecidos ao público por provedores como Azure, AWS, Google Cloud.

> Exemplo: Hospedar um site no Azure App Services.

#### • Nuvem Privada

Infraestrutura dedicada a uma única organização, seja no local ou hospedada.

> Exemplo: Azure Stack HCI em datacenter corporativo.

#### • Nuvem Híbrida

Combina ambientes de nuvem pública e privada.

> Exemplo: Backup local integrado ao Azure Backup na nuvem.

**📊 Comparativo**

| Modelo        | Custo Inicial | Flexibilidade | Controle |
| ------------- | ------------- | ------------- | -------- |
| Nuvem Pública | Baixo         | Alta          | Médio    |
| Nuvem Privada | Alto          | Média         | Alto     |
| Nuvem Híbrida | Médio         | Alta          | Alto     |


### 🔹 CapEx vs OpEx

* **CapEx (Capital Expenditure)**: Investimento inicial em equipamentos físicos.

  > Exemplo: Comprar servidores físicos.

* **OpEx (Operational Expenditure)**: Despesas operacionais contínuas.

  > Exemplo: Pagar mensalmente por uso de VM no Azure.


## ✅ Benefícios da Nuvem

| Benefício            | Descrição                                         | Exemplo                                        |
| -------------------- | ------------------------------------------------- | ---------------------------------------------- |
| Alta disponibilidade | Sistema projetado para operar continuamente.      | Azure garante SLA de até 99,99% em serviços.   |
| Escalabilidade       | Aumentar ou reduzir recursos conforme necessário. | Escalar um App Service durante picos.          |
| Elasticidade         | Ajuste automático de recursos.                    | Auto-scale de VMs conforme carga.              |
| Confiabilidade       | Redundância e failover para alta confiabilidade.  | VMs replicadas entre zonas de disponibilidade. |
| Previsibilidade      | Custo e desempenho previsíveis.                   | Tiers fixos em planos de serviço.              |
| Segurança            | Proteção de dados com compliance e criptografia.  | Azure Defender e RBAC.                         |
| Governança           | Controle de políticas e conformidade.             | Azure Policy e Blueprints.                     |
| Gerenciabilidade     | Ferramentas de monitoramento e automação.         | Azure Monitor, Log Analytics, Automation.      |


## 📦 Tipos de Serviço de Nuvem

### • IaaS - Infraestrutura como Serviço

> Exemplo: Azure Virtual Machines – você gerencia o SO, rede, discos, etc.

### • PaaS - Plataforma como Serviço

> Exemplo: Azure App Service – você gerencia a aplicação, a plataforma é gerida pelo Azure.

### • SaaS - Software como Serviço

> Exemplo: Microsoft 365 – o fornecedor gerencia tudo, você apenas usa.

### • Modelo de Responsabilidade Compartilhada

| Área | Responsabilidade do Cliente | Responsabilidade do Provedor |
| ---- | --------------------------- | ---------------------------- |
| IaaS | Alta                        | Baixa                        |
| PaaS | Média                       | Média                        |
| SaaS | Baixa                       | Alta                         |


## 🌍 Componentes de Arquitetura do Azure

* **Regiões**
  Localização geográfica dos datacenters.

  > Exemplo: Brazil South, East US.

* **Zonas de Disponibilidade**
  Conjuntos de datacenters com isolamento físico.

  > Exemplo: Alta disponibilidade para VMs.

* **Pares de Regiões**
  Regiões emparelhadas para recuperação de desastres.

  > Exemplo: Brazil South ↔ South Central US.

* **Regiões Soberanas do Azure**
  Datacenters isolados para conformidade local.

  > Exemplo: Azure Government (EUA), Azure China.

* **Recursos do Azure**
  Componentes gerenciáveis (VMs, redes, storage...).

* **Assinaturas e Grupos de Gerenciamento**
  Camadas para controle e organização de recursos.


## 🖥️ Computação e Rede

### • Criação de VM com Windows Server 2025 + DNS (PowerShell)

```powershell
New-AzResourceGroup -Name "rg-vm-demo" -Location "East US"

$cred = Get-Credential

New-AzVM -ResourceGroupName "rg-vm-demo" `
         -Name "vm-win2025" `
         -Location "East US" `
         -VirtualNetworkName "vnet-demo" `
         -SubnetName "subnet-demo" `
         -SecurityGroupName "nsg-demo" `
         -PublicIpAddressName "ip-demo" `
         -Credential $cred `
         -OpenPorts 3389 `
         -Image "Win2022Datacenter" `
         -Size "Standard_DS1_v2"
```

(Windows Server 2025 ainda pode ser referenciado via preview/image mais recente no catálogo.)

### • Serviços de Contêineres do Azure

* Azure Kubernetes Service (AKS)
* Azure Container Instances (ACI)
* Azure Container Apps


## 💾 Armazenamento

### • Domínio de objetivo

Tipos de dados: arquivos, blobs, tabelas, filas.

### • Redundância de Armazenamento

| Tipo | Descrição                        |
| ---- | -------------------------------- |
| LRS  | Redundância local (1 datacenter) |
| ZRS  | Redundância entre zonas          |
| GRS  | Redundância geográfica           |
| GZRS | Redundância geográfica + zonas   |

### • Serviços e Endpoints

* Blob Storage
* Queue Storage
* Table Storage
* File Storage

  > Endpoints: https\://<nome>.blob.core.windows.net/

### • Camadas de Acesso

* Hot: acesso frequente
* Cool: acesso esporádico
* Archive: acesso raro

### • Azure Data Box

Dispositivo físico para migração de grandes volumes de dados para a nuvem.


### 🛠️ Hands-on: Criar Armazenamento de Blobs (Terraform)

```hcl
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-storage-demo"
  location = "East US"
}

resource "azurerm_storage_account" "storage" {
  name                     = "storagedemoblob"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "container" {
  name                  = "meusblobs"
  storage_account_name  = azurerm_storage_account.storage.name
  container_access_type = "private"
}
```
