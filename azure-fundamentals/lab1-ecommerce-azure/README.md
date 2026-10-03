# Azure E-Commerce — Product Registration Application

![Azure](https://img.shields.io/badge/Microsoft_Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

A learning project that uses Terraform to provision Azure infrastructure and a Python/Streamlit web application to register and display products. Product records are stored in Azure SQL Database, and uploaded images are stored in Azure Blob Storage.

## Origin and Improvements

This project is an engineering improvement of **Lab 1: Storing E-Commerce Data in the Cloud**, completed during the **Microsoft Azure Cloud Native bootcamp from [DIO](https://www.dio.me/)**. It preserves the challenge's learning objective and application workflow while extending the original implementation with:

- reproducible Azure provisioning through Terraform;
- private Blob access and a client-specific SQL firewall rule;
- schema-based product validation and compensation for partial writes;
- repeatable database initialization and command-line evidence;
- automated Python and Terraform checks in GitHub Actions;
- documented deployment, validation, troubleshooting, and cleanup workflows.

## Overview and Architecture

The Streamlit application connects directly to Azure SQL Database using `pymssql` and uploads images using the Azure Storage SDK. It validates product data against the database limits before calling external services, stores image URLs alongside product data, and displays products in a three-column layout. The Streamlit server downloads private images using storage credentials and renders the resulting bytes. Azure SQL Database is the source of truth for product records.

Terraform provisions a resource group, an Azure SQL logical server and database, a storage account, a private Blob container, and a firewall rule for the supplied client IPv4 address. The application runs in the environment where Streamlit is started; the repository does not provision application hosting or a serverless compute deployment.

### Architecture Diagram

```text
       User browser                 Microsoft Azure
            |              +----------------------------------+
            | HTTP         | Resource Group                   |
            v              |                                  |
+------------------------+ | +------------------------------+ |
| Local workstation      | | | Azure SQL logical server     | |
|                        | | | - client IPv4 firewall rule  | |
| Streamlit / Python     |---|>| - SQL Database              | |
|       |                | | | - dbo.Produtos               | |
|       | Azure SDK      | | +------------------------------+ |
|       +----------------|-|>| Storage account              | |
|                        | | | - private Blob container     | |
| Terraform CLI ---------|-|>| - product images             | |
+------------------------+ | +------------------------------+ |
                           +----------------------------------+
             pymssql ----------> product metadata
             Azure SDK --------> authenticated image access
             AzureRM ----------> resource lifecycle
```

The browser communicates only with the local Streamlit process. The application writes product metadata to Azure SQL through `pymssql` and accesses the private Blob container with the Azure Storage SDK and application credentials. Terraform manages the Azure resources independently of the application request flow.

## Project Structure

```text
lab1-ecommerce-azure/
├── app/
│   ├── .env.example          # Configuration template; copy to .env
│   ├── .python-version      # Python 3.12
│   ├── config.py            # Shared environment loading and SQL settings
│   ├── main.py              # Streamlit application
│   ├── product_service.py   # Validation and cross-service registration workflow
│   ├── storage.py           # Authenticated private image download
│   ├── requirements.txt     # Validated dependency versions
│   └── database/
│       ├── init-db.py       # Python database initializer
│       ├── init-db.sh       # Wrapper for the Python initializer
│       ├── inspect-db.py    # CLI evidence for schema and stored records
│       └── init.sql         # Product table schema
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars.example
│   ├── tests/provisioning.tftest.hcl
│   ├── deploy.sh
│   └── destroy.sh
├── scripts/
│   ├── validate.sh          # Offline Python and Terraform checks
│   └── validate-live.sh     # Read-only checks against deployed services
├── tests/
│   ├── test_configuration.py
│   ├── test_product_service.py
│   └── test_storage.py
└── README.md
```

Local credentials, environment files, variable value files, and Terraform state are not part of the setup templates.

## Tech Stack

- **Infrastructure as code:** Terraform
- **Cloud provider:** Microsoft Azure
- **Database:** Azure SQL Database on an Azure SQL logical server
- **Image storage:** Azure Blob Storage
- **Web application:** Python and Streamlit
- **Database client:** `pymssql` for both the application and database initialization
- **Configuration loading:** `python-dotenv`
- **Version control:** Git/GitHub

## Provisioned Azure Resources

- Resource group
- Azure SQL logical server and database with the Basic SKU
- Standard storage account with locally redundant storage (LRS)
- Private Blob container
- SQL firewall rule named `AllowLabClient`, limited to one client IPv4 address

Anonymous Blob access is disabled at the account and container levels. The application downloads private images using its storage connection string. Stored URLs remain unsigned: opening one directly without credentials should not return the image.

SQL access is restricted to `client_ip_address`. Update this input and review another plan if your public IP changes. Application hosting and private network endpoints are outside this phase.

## Getting Started

### Requirements and Local Installation

- Python 3.12 (local verification used Python 3.12.3 on Linux)
- An Azure subscription with permission to create the lab resources
- Terraform 1.10 or later, below 2.0 ([download](https://www.terraform.io/downloads.html))
- Azure CLI installed and authenticated for provisioning

Run these commands from the repository root:

```bash
cd azure-fundamentals/lab1-ecommerce-azure
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r app/requirements.txt
python -m pip check
cp app/.env.example app/.env
```

The dependency list pins the complete set installed during phase 1. The Python initializer uses the same client as the application, so ODBC and `sqlcmd` are not required. Edit `app/.env` locally; never commit credentials.

### 1. Prepare and Review the Infrastructure

AzureRM 4.x and Random 3.x are declared explicitly, with exact versions recorded in the lockfile. The subscription ID is a Terraform input; see the [AzureRM provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/index).

Verify the subscription before preparing a live plan:

```bash
az login
az account list --query "[].{Name:name,Id:id,State:state}" --output table
az account set --subscription "YOUR_STUDENT_SUBSCRIPTION_ID"
az account show --query "{Name:name,Id:id,State:state}" --output table
```

Confirm the student offer and remaining credit in the Azure portal. Azure SQL availability depends on both the subscription and region. The live validation documented below succeeded with the Basic SKU in `brazilsouth`.

From the lab directory, create a local variable file. Git ignores `terraform.tfvars` and other `*.tfvars` files while retaining `*.tfvars.example` templates:

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit that file with the real subscription ID, a globally unique SQL server name, an allowed region, and your actual public IPv4 address. The example IP is a documentation placeholder. All Azure resources use the same `location`, which defaults to `brazilsouth`. This region was validated with the Azure for Students subscription used for this lab. The storage account name is optional: omitting it uses `prefix` plus a random suffix. When an explicit name is supplied, Terraform does not create an unused random resource.

Read the SQL password without displaying it or placing it in shell history:

```bash
read -rsp "SQL administrator password: " TF_VAR_sql_password
printf '\n'
export TF_VAR_sql_password
terraform -chdir=terraform init
terraform -chdir=terraform fmt -check -recursive
terraform -chdir=terraform validate
terraform -chdir=terraform test
terraform -chdir=terraform plan -var-file=terraform.tfvars -out=/tmp/lab1-phase2.tfplan
```

Terraform tests use mocked providers and do not create Azure resources. Review the new live plan before applying it. Saved plans contain environment-specific data and are ignored by Git.

After accepting the plan:

```bash
terraform -chdir=terraform apply /tmp/lab1-phase2.tfplan
terraform -chdir=terraform output
unset TF_VAR_sql_password
```

A fresh deployment with an explicit storage account name should create six resources: resource group, storage account, private container, SQL server, SQL database, and client firewall rule. When the storage name is omitted, Terraform also creates a random suffix. Existing state can produce a different plan. The SQL password is passed through a write-only argument and is not persisted in the plan or state. Storage access keys and other sensitive resource attributes can still exist in Terraform state, so keep state and saved plans local.

### 2. Configure Environment Variables

Edit `app/.env` using the values for your resources. Application and initializer both use:

| Variable | Expected value |
| -------- | -------------- |
| `SQL_SERVER` | Full SQL hostname, including `.database.windows.net` |
| `SQL_DATABASE` | Database name |
| `SQL_USERNAME` | SQL login |
| `SQL_PASSWORD` | SQL password |
| `AZURE_STORAGE_CONNECTION_STRING` | Storage connection string for uploads and private image reads |
| `AZURE_STORAGE_CONTAINER_NAME` | Provisioned private Blob container name |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account used to construct image URLs |

Map the nonsecret Terraform outputs to the local environment:

| Output | Environment variable |
| ------ | -------------------- |
| `sql_server_fqdn` | `SQL_SERVER` |
| `sql_database_name` | `SQL_DATABASE` |
| `sql_username` | `SQL_USERNAME` |
| `storage_account_name` | `AZURE_STORAGE_ACCOUNT_NAME` |
| `storage_container_name` | `AZURE_STORAGE_CONTAINER_NAME` |

Use the provisioning password for `SQL_PASSWORD`. Retrieve the storage connection string locally from the portal or this command, using the resource names from the outputs:

```bash
az storage account show-connection-string \
  --resource-group "YOUR_RESOURCE_GROUP" \
  --name "YOUR_STORAGE_ACCOUNT" \
  --query connectionString --output tsv
```

Copy the result to `app/.env`. Do not paste it into chat or validation reports. Terraform outputs do not expose passwords, keys, or connection strings; state still contains sensitive resource values.

Both programs load `app/.env` through an absolute path derived from their source location. Process environment values take precedence. Legacy `SQL_SERVER_NAME`, `SQL_DB_NAME`, and `SQL_USER` remain accepted as fallbacks; use the canonical names above for new configurations. The legacy server name must omit the domain suffix.

### 3. Initialize the Database

With the virtual environment active, run from the lab directory:

```bash
python app/database/init-db.py
```

Alternatively, `bash app/database/init-db.sh` invokes the same initializer using `python3` from the active environment. The SQL file is resolved relative to the initializer, regardless of the working directory. A configuration or database failure returns a nonzero exit status.

The schema creates `dbo.Produtos` with `id`, `nome`, `descricao`, `preco`, and `imagem_url` columns only when the table does not already exist. Repeated initialization preserves the table and its records.

### Optional Terraform Deployment Script

The deployment wrapper runs initialization, formatting, validation, planning, and an interactive apply from the correct Terraform directory:

```bash
read -rsp "SQL administrator password: " TF_VAR_sql_password
printf '\n'
export TF_VAR_sql_password
bash terraform/deploy.sh -var-file=terraform.tfvars
unset TF_VAR_sql_password
```

Additional arguments are passed directly to `terraform plan`. The script stops on the first failed command, never evaluates an application `.env` file as shell input, stores its plan temporarily outside the repository, and removes that plan when it exits.

### 4. Run the Application

From the lab directory, with the virtual environment active:

```bash
python -m streamlit run app/main.py
```

Open the local URL printed by Streamlit. Registration and listing require a reachable, initialized SQL database. Image uploads and display require the provisioned private container and matching storage credentials.

## Application Features

- Register products with a name, description, price, and optional image
- Validate product fields against the Azure SQL schema before upload
- Upload PNG and JPEG images with their original extension and MIME type
- Insert and retrieve product records in Azure SQL Database
- Remove a newly uploaded Blob when the corresponding SQL insert fails
- Display products in a three-column layout
- Check required name and description fields and enforce a nonnegative price through the Streamlit input
- Show success, warning, and error messages in the interface

The application interface, database fields, and script messages retain their original Portuguese names.

## Results and Demonstration

The screenshots below were regenerated from the phase 2 deployment in `brazilsouth`. They provide evidence of the deployed resources, database schema, and application workflow. The accompanying CLI commands reproduce the SQL record and private Blob queries without requiring additional screenshots. These results do not represent availability guarantees or production readiness.

### 1. Infrastructure Provisioned with Terraform

List the resources tracked by Terraform:

```bash
terraform -chdir=terraform state list
```

Query the deployed Azure resources directly from the resource group:

```bash
az resource list \
  --resource-group "$(terraform -chdir=terraform output -raw resource_group_name)" \
  --query "sort_by([].{Name:name,Type:type,Location:location}, &Type)" \
  --output table
```

The Terraform state includes the resource group and private Blob container. The Azure query provides independent evidence of the resources currently available through Azure Resource Manager.

<figure style="text-align: center;">
    <img src="./docs/image/00-figure-azure-recurse.png" alt="Azure resource inventory for the e-commerce lab" width="859">
    <figcaption>Figure 1: Live Azure Resource Manager inventory showing the SQL logical server, automatically created master database, application database, and storage account in Brazil South.</figcaption>
</figure>

### 2. Database Schema

Inspect the deployed `dbo.Produtos` schema through `INFORMATION_SCHEMA.COLUMNS`:

```bash
python app/database/inspect-db.py schema
```

The command uses the same `app/.env` or process environment configuration as the application and does not print credentials.

<figure style="text-align: center;">
    <img src="./docs/image/01-figure-azure-bd.png" alt="Produtos table schema returned by the database inspection command" width="500">
    <figcaption>Figure 2: Live `INFORMATION_SCHEMA.COLUMNS` query showing the columns, data types, limits, and nullability of `dbo.Produtos`.</figcaption>
</figure>

### 3. Application Interface

<figure style="text-align: center;">
    <img src="./docs/image/02-figure-app-result.png" alt="Successful product registration and authenticated image display in Streamlit" width="758">
    <figcaption>Figure 3: Successful Streamlit registration followed by product details and an image read from the private Blob container.</figcaption>
</figure>

### 4. Stored Data and Images

Query the product records stored in Azure SQL Database:

```bash
python app/database/inspect-db.py products
```

List the image Blobs stored in the private container:

```bash
az storage blob list \
  --container-name "$AZURE_STORAGE_CONTAINER_NAME" \
  --connection-string "$AZURE_STORAGE_CONNECTION_STRING" \
  --query "[].{Name:name,SizeBytes:properties.contentLength,ContentType:properties.contentSettings.contentType,Modified:properties.lastModified}" \
  --output table
```

These commands provide live CLI evidence for the relational records and their corresponding image objects. Keep the connection string in an environment variable and never include it in screenshots or command output.

## Engineering Concepts Demonstrated

This lab demonstrates infrastructure as code, use of managed Azure data services, relational data persistence, and SDK integration for image uploads. Terraform provides a declarative infrastructure definition, while the application separates image storage from product metadata.

## Testing and Observability

Run every offline Python and Terraform check from the lab directory:

```bash
./scripts/validate.sh
```

The script verifies installed Python dependencies, runs the 17 unit tests, initializes Terraform without a remote backend, checks formatting and configuration, and runs the six mocked Terraform tests. The path-scoped GitHub Actions workflow in `.github/workflows/lab1-quality.yml` runs the same script on pushes and pull requests without Azure credentials.

For repeatable validation against an existing deployment, provide the write-only SQL value required by Terraform and run:

```bash
read -rsp "SQL administrator password: " TF_VAR_sql_password
printf '\n'
export TF_VAR_sql_password

./scripts/validate-live.sh terraform.tfvars

unset TF_VAR_sql_password
```

The live script requires an authenticated Azure CLI session and the SQL settings in `app/.env`. It obtains the storage resource names from Terraform outputs and retrieves the connection string directly through Azure CLI without printing it. It fails on Terraform drift or public container access, initializes the database twice, prints the live schema and products, and reports Blob metadata. It does not create products, upload images, apply Terraform changes, or print credentials. The Streamlit registration workflow remains a manual interface check.

The application reports operation results through Streamlit messages. Monitoring, dashboards, and health check endpoints are outside this lab.

## Improvement Phases and Validation Status

| Phase | Scope | Status |
| ----- | ----- | ------ |
| 1 | Local installation, dependency versions, shared configuration, initializer paths, and setup documentation | Verified on Python 3.12.3 |
| 2 | Complete Terraform provisioning, connection outputs, network access, and image access | Validated locally and in Azure on October 2, 2026 |
| 3 | Consistent SQL and Blob writes, schema-based field validation, image metadata, and removal of local JSON writes | Validated locally and in Azure on October 2, 2026 |
| 4 | Git ignore rules, generated artifacts, deployment error handling, and repeatable initialization | Validated locally and in Azure on October 2, 2026 |
| 5 | Automated checks, repeatable end-to-end validation, and resource cleanup | Validated locally and in Azure on October 2, 2026; CI awaits first push |

The screenshots above were regenerated after the successful phase 2 deployment.

### Phase 2 Validation Procedure

1. Run the Python tests, Terraform formatting check, validation, and six mocked Terraform tests.
2. Verify the student subscription and review a newly generated plan; share its resource summary and redacted errors before applying.
3. After plan review, apply and confirm the container is private and SQL access matches the client IP.
4. Configure `app/.env`, initialize the database once, and start Streamlit. Register a product with an image and verify that listing displays the record and image.
5. Open the stored Blob URL without credentials: it must not return the image. Confirm that the same image renders inside Streamlit.

The application uses the authenticated download described in the [Azure Blob client documentation](https://learn.microsoft.com/python/api/azure-storage-blob/azure.storage.blob.blobclient).

### Phase 2 Validation Result

Live validation completed on October 2, 2026, using an Azure for Students subscription in `brazilsouth`:

- Terraform created six resources in one apply: resource group, Standard LRS storage account, private Blob container, Azure SQL logical server, Basic SQL database, and a client-specific SQL firewall rule.
- Database initialization completed through `pymssql` using the provisioned SQL endpoint.
- Streamlit inserted and listed a product stored in Azure SQL Database.
- The application uploaded an image to the private `products` container and rendered it through an authenticated server-side download.
- An anonymous request to the same Blob URL returned HTTP `409`, confirming that public Blob access was disabled.
- Eight Python tests and six mocked Terraform tests passed locally.

Phase 2 exposed that descriptions longer than the `NVARCHAR(255)` column failed after image upload, leaving an orphaned Blob and a divergent local JSON entry. Phase 3 resolves this by validating schema limits before upload, removing automatic JSON persistence, preserving image extension and MIME type, and deleting a newly uploaded Blob when SQL insertion fails.

### Phase 3 Validation Procedure

1. Run the 17 offline tests and confirm the Streamlit application starts without an initialization error.
2. Submit a product description with 256 characters and an image. The interface must reject it before SQL or Blob Storage changes.
3. Register a valid product using a PNG or JPEG image. Confirm the SQL record and private image appear in Streamlit.
4. List the container with the CLI command above. The new Blob must retain its original extension and report `image/png` or `image/jpeg` instead of `application/octet-stream`.
5. Simulate an unavailable SQL database while keeping valid Storage credentials, then attempt a registration with an image. The interface must report the database failure and the Blob count must remain unchanged after compensation.
6. Confirm that registration no longer creates or updates `produtos.json`.

Live validation completed on October 2, 2026:

- All 17 automated tests passed, including rejection of schema length violations before any external service call.
- A valid product was stored in Azure SQL Database and listed by the application.
- Its uploaded image retained the `.png` extension and reported `image/png` as its Blob content type.
- A forced SQL failure left the Blob count unchanged at two, confirming successful compensation without an orphaned image.
- Product registration did not recreate `produtos.json`, leaving Azure SQL Database as the source of truth.

### Phase 4 Validation Result

Validation completed on October 2, 2026:

- All 17 Python tests and six mocked Terraform tests passed; Terraform formatting and configuration validation also succeeded.
- Git ignore rules matched the local state, state backup, and variable file while keeping the example and provider lock files versioned.
- Running the database initializer twice against the existing Azure SQL database completed successfully and left the product query unchanged.
- The deployment wrapper refreshed the six managed resources, reported no infrastructure changes, accepted a negative confirmation, and exited without applying the saved plan.
- Historical saved plans were removed from version control, and newly generated plans are temporary and ignored.

## Resource Cleanup

Destroy the lab after capturing evidence and pushing the final commit to avoid continued Azure for Students usage. First verify the selected subscription and review a saved destruction plan:

```bash
az account show --query '{Name:name,Id:id,State:state}' --output table
RESOURCE_GROUP="$(terraform -chdir=terraform output -raw resource_group_name)"
read -rsp "SQL administrator password: " TF_VAR_sql_password
printf '\n'
export TF_VAR_sql_password

./terraform/destroy.sh -var-file=terraform.tfvars

unset TF_VAR_sql_password
```

The wrapper creates a temporary destruction plan and applies it only when `DESTROY` is entered exactly. Any other response cancels the operation. Removing the resource group also permanently removes the lab database and stored images, so retain the README evidence before confirming.

After a successful destruction, verify both Terraform state and Azure Resource Manager:

```bash
terraform -chdir=terraform state list
az group exists --name "$RESOURCE_GROUP"
unset RESOURCE_GROUP
```

The state command should print no resources and the Azure CLI command should return `false`.

### Phase 5 Validation Result

Validation completed on October 2, 2026:

- The consolidated offline script passed dependency checks, all 17 Python tests, Terraform formatting and validation, and all six mocked Terraform tests.
- The live script found no Terraform drift and listed all six managed resources.
- Two consecutive database initializations completed successfully before the script queried the deployed schema and existing products.
- The script retrieved storage credentials through Azure CLI, confirmed that the Blob container had no public access, and listed the stored image metadata.
- The cleanup wrapper generated a plan for exactly six resource deletions and cancelled safely when the confirmation did not match `DESTROY`.
- The path-scoped GitHub Actions workflow is ready for validation on the first push containing this phase.

## Troubleshooting Partial Deployments

If creation fails with `RequestDisallowedByAzure`, inspect the subscription's Azure Policy assignments and select an allowed region. This lab intentionally deploys the resource group, Storage, and SQL in one region.

If SQL creation reports a missing administrator password, verify locally that `TF_VAR_sql_password` contains a nonempty value and that a local variable file does not override it with an empty password. The configuration rejects empty passwords during planning. Generate a new plan after fixing the inputs; do not reuse the previously applied plan.

If SQL returns `ProvisioningDisabled` in a policy-allowed region, the SQL service has a separate regional restriction. Select another region allowed by the subscription and rebuild the lab there, or follow Microsoft's [SQL regional access request procedure](https://learn.microsoft.com/en-us/azure/azure-sql/database/quota-increase-request#enable-subscription-access-to-a-region). A successful Terraform plan does not prove that SQL provisioning is enabled in a region.

## Contributing

Contributions are welcome through issues and pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Jacivaldo Carvalho**
Telecommunications Engineer | DevOps | SRE | Networking
