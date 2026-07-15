terraform {
  required_version = ">= 1.5"
  required_providers {
    supabase = {
      source  = "supabase/supabase"
      version = "~> 1.0"
      # NOTE: The Supabase Terraform provider is currently in alpha.
      # Some attributes (e.g., service_role_key) may not be available yet.
      # If provisioning fails, use the Supabase CLI or Dashboard instead:
      #   supabase projects create --org-id <org> --db-password <pw>
      # Track provider stability: https://github.com/supabase/terraform-provider-supabase
    }
    vercel = {
      source  = "vercel/vercel"
      version = "~> 1.0"
    }
  }
}

provider "supabase" {
  access_token = var.supabase_access_token
}

provider "vercel" {
  api_token = var.vercel_api_token
}
