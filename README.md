# 🧠 Microsoft Azure Cloud Native Bootcamp

<p align="center">
  <img src="https://assets.dio.me/aKHRJVQ-Pr_wi1kX_C17yNCh-3oQiZYwW-0XIEnxpwQ/f:webp/h:120/q:80/L3RyYWNrcy9kNzNlZTNlMy00MWExLTRiOTAtYmZkZi1mOGZhYjQzMmE1MDAucG5n" alt="Bootcamp logo" />
</p>

Learning notes, hands-on experiments, and code developed during the **Microsoft Azure Cloud Native Bootcamp**, offered by [DIO](https://www.dio.me/) in partnership with **Microsoft**.

## Overview

This repository records my learning and provides a reference for Azure services and application development practices. The committed material currently includes Azure fundamentals notes and an e-commerce product registration lab.

The lab combines a Python/Streamlit application with Azure SQL Database and Azure Blob Storage. Terraform provisions the resource group, SQL server, database, and storage account. See the [lab documentation](azure-fundamentals/lab1-ecommerce-azure/README.md) for architecture, setup instructions, and implementation limitations.

## 📚 Bootcamp Curriculum

The curriculum covers the following topics. This list describes the bootcamp scope; it does not imply that every topic has an implementation in this repository.

### 🔹 Azure Platform Fundamentals

* Introduction to the Microsoft Azure Cloud Native Experience (completed)
* Azure Application Platform Fundamentals
* Challenge: Storing E-Commerce Data in the Cloud
* Mentoring: Launch Livestream with Microsoft Experts

### 🔹 Containers and Orchestration on Azure

* Orchestration with Azure Kubernetes Service (AKS)
* Working with AKS and Kubernetes
* Web Applications with Azure App Service
* Coding and Computational Logic Challenges
* Hands-on Challenge with AKS and App Service

### 🔹 Development and Hosting with Azure ML

* Containerized Applications with Azure Container Apps
* Challenge: Creating a Blog with Container Apps
* Challenge: Publishing and Scaling Applications

### 🔹 API Management and Security

* Management with Azure API Management
* Project: Secure Payment API
* Challenge: Protecting Your API

### 🔹 Serverless Computing and Automation

* Serverless Computing with Azure Functions
* Challenge: Payment Slip Authentication Service

### 🔹 Artificial Intelligence in Development

* GitHub Copilot in Development
* Project: Configuring GitHub Copilot with VS Code

### 🔹 Building a Cloud-Native Application

* Final Project: Cloud-Native Car Rental Application
* Bootcamp Assessment

## 📁 Repository Organization

The planned module layout is shown below. It is retained from the original documentation and includes directories intended for future work; the committed content currently resides in the Azure fundamentals module.

```bash
📦 bootcamp-azure-cloud-native
 ┣ 📂 azure-fundamentals
 ┣ 📂 conteinerizacao-aks
 ┣ 📂 azure-container-apps
 ┣ 📂 api-management
 ┣ 📂 serverless-functions
 ┣ 📂 ia-e-copilot
 ┣ 📂 aplicacao-cloud-native
 ┗ 📄 README.md
```

Available documentation:

* [Azure application platform fundamentals](azure-fundamentals/01-fundamentos-plataforma-app-azure.md)
* [Azure e-commerce product registration lab](azure-fundamentals/lab1-ecommerce-azure/README.md)

## 🛠️ Technologies and Tools

The implemented lab uses **Microsoft Azure**, **Azure SQL Database**, **Azure Blob Storage**, **Terraform**, **Python**, and **Streamlit**. Its Python integrations use the Azure Storage SDK and database clients.

The broader curriculum also covers **Azure Kubernetes Service (AKS)**, **Azure App Service**, **Azure API Management**, **Azure Functions**, **Azure Container Apps**, **GitHub Copilot**, **Visual Studio Code**, and container tooling such as **Docker** and **Kubernetes**. These are curriculum topics rather than additional implemented capabilities.

## 💡 Learning Goals and Engineering Value

Build practical knowledge of cloud computing and Azure application architecture through hands-on exercises. The current lab demonstrates infrastructure as code, integration with managed cloud storage and a relational database, and a web interface for registering and listing products.

## Author and License

Created by Jacivaldo Carvalho. Licensed under the MIT License; see [LICENSE](LICENSE).
