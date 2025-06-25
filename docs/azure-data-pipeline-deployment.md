# Azure Data Pipeline Deployment Guide

This guide explains how to deploy your event-driven data processing pipeline using Azure CLI **and** the Azure Portal. The system includes:

- **Event source:** Azure Event Hubs
- **Processing engine:** Apache Spark (on Azure Container Apps)
- **Storage:** Azure Data Lake Gen2 (via abfss)
- **Simulated event generator:** Python app deployed as container

---

## 1. Infrastructure Components

| Component            | Technology           |
|---------------------|----------------------|
| Stream source        | Azure Event Hubs     |
| Stream processor     | Apache Spark         |
| Storage              | Azure Data Lake Gen2 |
| Container platform   | Azure Container Apps |
| Image registry       | Azure Container Registry (ACR) |

---

## 2. Deployment Options

- [2.1 Azure CLI (recommended for automation)](#21-azure-cli-deployment)
- [2.2 Azure Portal (manual + visual)](#22-azure-portal-deployment)

---

## 2.1 Azure CLI Deployment

### 🔐 Prerequisites

- Azure CLI ≥ 2.45.0
- Logged in with `az login`
- Proper role access (Contributor + AcrPull)

---

### ✅ Step-by-Step via CLI

#### 1. Create Resource Group

```bash
az group create --name spark-resources --location eastus
```

#### 2. Create Azure Storage Account + Filesystem

```bash
az storage account create   --name sparkdatalake250623   --resource-group spark-resources   --location eastus   --sku Standard_LRS   --kind StorageV2   --hierarchical-namespace true

az storage fs create   --account-name sparkdatalake250623   --name spark-output
```

#### 3. Create Azure Event Hub Namespace and Topic

```bash
az eventhubs namespace create   --name spark-eh-ns   --resource-group spark-resources   --location eastus   --tags "Ambiente=dev" "Centro de Costo=Ingeniería" "Creado Por=majimeno@uninorte.edu.co" "Responsable=majimeno@uninorte.edu.co" "Fecha de Creación=2025-06-23"

az eventhubs eventhub create   --name spark-topic   --namespace-name spark-eh-ns   --resource-group spark-resources
```

#### 4. Create ACR and Push Images

```bash
az acr create --name sparkacr001 --resource-group spark-resources --sku Basic --admin-enabled true

az acr login --name sparkacr001
docker tag netflix-sim sparkacr001.azurecr.io/netflix-sim:latest
docker push sparkacr001.azurecr.io/netflix-sim:latest
```

#### 5. Create Container Apps Environment

```bash
az containerapp env create   --name spark-env   --resource-group spark-resources   --location eastus   --tags "Ambiente=dev" "Centro de Costo=Ingeniería" "Creado Por=majimeno@uninorte.edu.co" "Responsable=majimeno@uninorte.edu.co" "Fecha de Creación=2025-06-23"
```

#### 6. Create Spark and Simulator Apps

Use `az containerapp create` or `az containerapp up --yaml spark-containerapp.yaml`.

> ⚠️ Ensure you assign the `AcrPull` role to the container app identity:
```bash
az containerapp identity assign --name netflix-sim --resource-group spark-resources --system-assigned

az role assignment create   --assignee <principalId>   --role AcrPull   --scope $(az acr show --name sparkacr001 --query id --output tsv)
```

---

## 2.2 Azure Portal Deployment

1. **Create Resource Group**
   - Go to Azure Portal → Resource groups → "Create"

2. **Create Azure Storage**
   - Use "Storage accounts" → "Create"
   - Enable *Hierarchical namespace* for ADLS Gen2

3. **Create Event Hub Namespace and Topic**
   - Go to "Event Hubs" → "+ New namespace"
   - After creation, create a new Event Hub (topic)

4. **Create ACR**
   - "Container Registries" → "+ Create"
   - Enable admin access
   - Push Docker images using local Docker login

5. **Create Container Apps Environment**
   - Go to "Container Apps" → "+ Environment"
   - Choose existing RG and region

6. **Create Container Apps (Spark + Simulator)**
   - Use wizard to:
     - Set image from ACR
     - Define environment variables
     - Link to Container Apps Environment

7. **Grant ACR Pull Access**
   - Go to "Access Control (IAM)" on ACR
   - Assign **AcrPull** role to the container app's managed identity

---

## 3. Monitoring

- `az containerapp logs show --name spark-env --resource-group spark-resources`
- Event Hub Metrics → Monitor ingress
- Storage Explorer → ADLS output folder: `abfss://spark-output@.../events/`

---

## 4. Troubleshooting

| Symptom                           | Likely Cause                          | Fix |
|----------------------------------|---------------------------------------|-----|
| No replica found                 | Image pull error or crash             | Confirm ACR access + logs |
| Spark stops silently             | No data in Event Hub                  | Check simulator is running |
| abfss path error                 | Missing Hadoop ABFS connector         | Use Spark base image with connector |
| Authentication error             | Invalid `AZURE_CLIENT_SECRET`         | Double-check secrets |

---

Let me know if you'd like a companion `.env`, `spark-containerapp.yaml`, or a dashboard setup!