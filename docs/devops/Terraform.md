# Infrastructure as Code — Terraform

## Document Control

| Field | Value |
|---|---|
| Document ID | DVO-TERRA-013 |
| Version | 1.0.0 |
| Status | Draft |
| Date | 2026-07-10 |
| Classification | Internal |
| Owner | Developer |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [IaC Maturity](#2-iac-maturity)
3. [Terraform Directory Structure](#3-terraform-directory-structure)
4. [Provider Configuration](#4-provider-configuration)
5. [Remote State Management](#5-remote-state-management)
6. [Supabase Resources](#6-supabase-resources)
7. [Vercel Resources](#7-vercel-resources)
8. [Environment Variables](#8-environment-variables)
9. [Variable Definitions](#9-variable-definitions)
10. [Outputs](#10-outputs)
11. [Module Structure](#11-module-structure)
12. [Workspace Strategy](#12-workspace-strategy)
13. [CI/CD Integration](#13-cicd-integration)
14. [Security Considerations](#14-security-considerations)
15. [Cost Tracking](#15-cost-tracking)
16. [Testing Strategy](#16-testing-strategy)
17. [Edge Cases](#17-edge-cases)
18. [Failure Scenarios](#18-failure-scenarios)
19. [Migration Guide](#19-migration-guide)
20. [References](#20-references)

---

## 1. Executive Summary

Terraform provides Infrastructure as Code (IaC) for Second Brain OS cloud resources. It manages Supabase projects, Vercel deployments, and DNS configuration declaratively. Current maturity is Level 2 (Scripted), targeting Level 3 (Declarative) by Q1 2027.

---

## 2. IaC Maturity

| Level | State | Tools | Status |
|---|---|---|---|
| 1 — Manual | All resources via dashboards | None | ✅ Past |
| 2 — Scripted | Resources via CLI scripts | Shell, Supabase CLI | ✅ Current |
| **3 — Declarative** | **Resources defined in Terraform** | **Terraform, OpenTofu** | **⏳ Target Q1 2027** |
| 4 — Automated | CI/CD manages infrastructure | Terraform Cloud | ⏳ 2027+ |
| 5 — GitOps | Infra changes via PRs | ArgoCD, Crossplane | ⏳ Vision |

---

## 3. Terraform Directory Structure

```
infrastructure/
├── terraform/
│   ├── environments/
│   │   ├── production/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── terraform.tfvars
│   │   └── staging/
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── terraform.tfvars
│   ├── modules/
│   │   ├── frontend/
│   │   ├── backend/
│   │   ├── database/
│   │   └── monitoring/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── docker/
└── kubernetes/
```

---

## 4. Provider Configuration

```hcl
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    vercel = {
      source  = "vercel/vercel"
      version = "~> 0.15"
    }
    supabase = {
      source  = "supabase/supabase"
      version = "~> 0.3"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "vercel" {
  api_token = var.vercel_api_token
}

provider "supabase" {
  access_token = var.supabase_access_token
}
```

---

## 5. Remote State Management

State is stored in an S3-compatible backend with DynamoDB locking:

```hcl
terraform {
  backend "s3" {
    bucket         = "secondbrain-terraform-state"
    key            = "environments/production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}
```

| State File | Environment | Region |
|---|---|---|
| `environments/production/terraform.tfstate` | Production | us-east-1 |
| `environments/staging/terraform.tfstate` | Staging | us-east-1 |

---

## 6. Supabase Resources

```hcl
resource "supabase_project" "main" {
  name              = "secondbrain-os-${var.environment}"
  organization_id   = var.supabase_org_id
  database_password = var.supabase_db_password
  region            = "us-east-1"
  plan              = var.environment == "production" ? "pro" : "free"

  lifecycle {
    prevent_destroy = true
  }
}

resource "supabase_project_settings" "main" {
  project_ref = supabase_project.main.id
  auth_site_url = var.environment == "production"
    ? "https://app.secondbrainos.com"
    : "https://staging.secondbrainos.com"
}
```

---

## 7. Vercel Resources

```hcl
resource "vercel_project" "frontend" {
  name            = "secondbrain-frontend-${var.environment}"
  framework       = "nextjs"
  root_directory  = "apps/web"
  build_command   = "npm run build"
  output_directory = ".next"
  install_command = "npm ci"
}

resource "vercel_domain" "frontend" {
  count      = var.environment == "production" ? 1 : 0
  project_id = vercel_project.frontend.id
  domain     = "app.secondbrainos.com"
}
```

---

## 8. Environment Variables

```hcl
resource "vercel_project_environment_variable" "supabase_url" {
  project_id = vercel_project.frontend.id
  key        = "NEXT_PUBLIC_SUPABASE_URL"
  value      = supabase_project.main.public_url
  target     = ["production", "preview"]
}

resource "vercel_project_environment_variable" "supabase_anon_key" {
  project_id = vercel_project.frontend.id
  key        = "NEXT_PUBLIC_SUPABASE_ANON_KEY"
  value      = supabase_project.main.anon_key
  target     = ["production", "preview"]
  sensitive  = true
}
```

---

## 9. Variable Definitions

| Variable | Type | Sensitive | Description |
|---|---|---|---|
| `environment` | `string` | No | `staging` or `production` |
| `project_name` | `string` | No | Resource naming prefix |
| `vercel_api_token` | `string` | Yes | Vercel API token |
| `supabase_access_token` | `string` | Yes | Supabase access token |
| `supabase_db_password` | `string` | Yes | Database admin password |
| `supabase_org_id` | `string` | No | Supabase organization UUID |

---

## 10. Outputs

```hcl
output "frontend_url" {
  value = var.environment == "production"
    ? "https://app.secondbrainos.com"
    : "https://staging.secondbrainos.com"
}

output "backend_url" {
  value = var.environment == "production"
    ? "https://api.secondbrainos.com"
    : "https://staging-api.secondbrainos.com"
}

output "supabase_project_ref" {
  value = supabase_project.main.id
}
```

---

## 11. Module Structure

Each module encapsulates a complete component:

```
modules/
├── frontend/     # Vercel project, domain, env vars
├── backend/      # Railway project (via provider or CLI)
├── database/     # Supabase project, settings, backups
└── monitoring/   # Monitoring stack (planned)
```

---

## 12. Workspace Strategy

```bash
# Create workspaces per environment
terraform workspace new staging
terraform workspace new production

# Select workspace and apply
terraform workspace select staging
terraform apply -var-file=environments/staging/terraform.tfvars

terraform workspace select production
terraform apply -var-file=environments/production/terraform.tfvars
```

---

## 13. CI/CD Integration

Planned GitHub Actions workflow for Terraform:

```yaml
name: Terraform
on:
  push:
    paths:
      - "infrastructure/terraform/**"
  pull_request:
    paths:
      - "infrastructure/terraform/**"

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - run: terraform fmt -check
      - run: terraform init
      - run: terraform validate
      - run: terraform plan
```

---

## 14. Security Considerations

- Remote state encrypted at rest (S3 AES-256)
- State file contains secrets — access restricted via IAM
- `prevent_destroy` on production database
- Sensitive variables marked as `sensitive = true`
- Terraform plan reviewed before apply
- No hardcoded secrets in `.tf` files

---

## 15. Cost Tracking

| Resource | Estimated Monthly Cost |
|---|---|
| S3 state bucket | $0.10 |
| DynamoDB lock table | $0.10 |
| **Total** | **~$0.20** |

Resource costs (Supabase, Vercel, Railway) are tracked separately in `docs/devops/27_DevOps.md`.

---

## 16. Testing Strategy

| Test | Tool | Scope |
|---|---|---|
| Formatting | `terraform fmt -check` | All `.tf` files |
| Validation | `terraform validate` | Syntax + provider validation |
| Plan | `terraform plan` | Verify expected changes |
| Compliance | `terraform-compliance` | Policy as code (future) |

---

## 17. Edge Cases

- State file corruption → Use DynamoDB lock table to prevent concurrent writes
- Provider API deprecation → Pin provider versions with `~>` constraints
- Resource already exists → Use `import` to bring under Terraform management
- Environment drift → Run `terraform plan` periodically to detect drift
- `prevent_destroy` blocking → Remove cautiously, plan ahead for teardown

---

## 18. Failure Scenarios

| Scenario | Impact | Mitigation |
|---|---|---|
| State file locked | Can't apply | Wait for lock to release or force unlock |
| Provider rate limit | Plan/apply fails | Retry with backoff |
| Resource deletion by accident | Data loss | `prevent_destroy` on critical resources |
| Terraform version mismatch | State incompatibility | Pin versions with `required_version` |

---

## 19. Migration Guide

```bash
# Current state (Level 2 — Scripted):
#   - Supabase: Created via dashboard
#   - Vercel: Created via dashboard
#   - Railway: Created via dashboard

# Migration steps to Level 3:
1. Create Terraform configuration for each resource
2. Run `terraform import` for existing resources
3. Verify `terraform plan` shows no changes
4. Update CI/CD to run Terraform on infrastructure changes
5. Remove manual provisioning from runbooks
```

---

## 20. References

| Resource | URL / Location |
|---|---|
| Terraform Docs | https://developer.hashicorp.com/terraform |
| Vercel Provider | https://registry.terraform.io/providers/vercel/vercel |
| Supabase Provider | https://registry.terraform.io/providers/supabase/supabase |
| Deployment Strategy | `docs/devops/26_Deployment.md` |
| Infrastructure Overview | `docs/devops/Infrastructure.md` |
