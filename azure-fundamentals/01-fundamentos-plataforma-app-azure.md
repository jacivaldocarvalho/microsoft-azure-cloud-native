# Azure Application Platform Fundamentals

Course notes and illustrative examples. The commands below are preserved from the original material; they are separate from the e-commerce lab configuration.

## Cloud Computing

### What Is Cloud Computing?

Cloud computing delivers on-demand IT services over the internet with usage-based pricing. It provides access to compute, storage, networking, and other resources without requiring investment in on-premises infrastructure.

### Cloud Deployment Models

#### Public Cloud

Services available to customers through providers such as Azure, AWS, and Google Cloud.

> Example: Hosting a website on Azure App Service.

#### Private Cloud

Infrastructure dedicated to a single organization, either on premises or hosted externally.

> Example: Azure Stack HCI in a corporate data center, as described in these course notes.

#### Hybrid Cloud

Combines public and private cloud environments.

> Example: On-premises backups integrated with Azure Backup.

**Comparison**

| Model | Upfront Cost | Flexibility | Control |
| ----- | ------------ | ----------- | ------- |
| Public cloud | Low | High | Medium |
| Private cloud | High | Medium | High |
| Hybrid cloud | Medium | High | High |

### CapEx vs. OpEx

* **CapEx (Capital Expenditure)**: Upfront investment in physical equipment.

  > Example: Purchasing physical servers.

* **OpEx (Operating Expenditure)**: Ongoing operational expenses.

  > Example: Paying monthly for Azure virtual machine usage.

## Cloud Benefits

| Benefit | Description | Example |
| ------- | ----------- | ------- |
| Availability | Designing services to remain accessible. | Service-specific Azure availability commitments. |
| Scalability | Increasing or decreasing resources as needed. | Scaling an App Service during traffic peaks. |
| Elasticity | Automatically adjusting resources to demand. | Scaling virtual machines based on workload. |
| Reliability | Using redundancy and failover. | Replicating virtual machines across availability zones. |
| Predictability | Planning costs and performance. | Fixed service plan tiers. |
| Security | Protecting data through access controls and encryption. | Defender services and RBAC. |
| Governance | Managing policies and compliance. | Azure Policy and the Azure Blueprints example from the course notes. |
| Manageability | Monitoring and automating resource operations. | Azure Monitor, Log Analytics, and Automation. |

## Cloud Service Models

### IaaS — Infrastructure as a Service

> Example: Azure Virtual Machines — you manage the operating system, network configuration, disks, and other workload components.

### PaaS — Platform as a Service

> Example: Azure App Service — you manage the application, while Azure manages the platform.

### SaaS — Software as a Service

> Example: Microsoft 365 — the provider manages the software and underlying infrastructure; customers remain responsible for their data and access settings.

### Shared Responsibility Model

| Model | Customer Responsibility | Provider Responsibility |
| ----- | ----------------------- | ----------------------- |
| IaaS | High | Low |
| PaaS | Medium | Medium |
| SaaS | Low | High |

These comparisons are simplified learning aids. Responsibilities depend on the service and configuration.

## Azure Architecture Components

* **Regions**  
  Geographic locations containing data centers.

  > Example: Brazil South, East US.

* **Availability Zones**  
  Physically separate groups of data centers within a region.

  > Example: Deploying virtual machines across zones to support availability.

* **Region Pairs**  
  Paired regions that can support disaster recovery planning.

  > Example: Brazil South ↔ South Central US.

* **Azure Sovereign Regions**  
  Isolated cloud environments designed for specific regulatory requirements.

  > Example: Azure Government (United States), Azure China.

* **Azure Resources**  
  Manageable components such as virtual machines, networks, and storage.

* **Subscriptions and Management Groups**  
  Management layers for organizing and controlling resources.

## Compute and Networking

### Creating a Windows Server VM (PowerShell)

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

The preserved example selects the Windows Server 2022 image through the image argument. It does not install or configure DNS; the original heading referred to Windows Server 2025 and DNS, which the command does not demonstrate.

### Azure Container Services

* Azure Kubernetes Service (AKS)
* Azure Container Instances (ACI)
* Azure Container Apps

## Storage

### Storage Data Types

Data types include files, blobs, tables, and queues.

### Storage Redundancy

| Type | Description |
| ---- | ----------- |
| LRS | Local redundancy within one data center |
| ZRS | Redundancy across availability zones |
| GRS | Geographic redundancy |
| GZRS | Geographic and availability zone redundancy |

### Services and Endpoints

* Blob Storage
* Queue Storage
* Table Storage
* File Storage

> Endpoints: `https://<nome>.blob.core.windows.net/`

### Access Tiers

* Hot: frequent access
* Cool: infrequent access
* Archive: rarely accessed data

### Azure Data Box

A physical device for transferring large volumes of data to the cloud.

### Hands-on: Creating Blob Storage (Terraform)

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