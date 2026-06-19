# Note: The Supabase Terraform provider (supabase/supabase) is currently in alpha.
# Project provisioning is best done via the Supabase CLI or Management API.
# This file documents the intended infrastructure state.

locals {
  # Retrieve via: supabase projects list
  # Set in terraform.tfvars or CI environment
  project_ref = var.supabase_organization_id
}

# Database migrations are applied via the Supabase CLI:
#   supabase link --project-ref <ref>
#   supabase db push
#
# RLS policies are defined in ./apps/api/supabase/migrations/
#
# Auth providers (Google OAuth) configured via Supabase Dashboard:
#   https://supabase.com/dashboard/project/<ref>/auth/providers

resource "supabase_project" "main" {
  name              = var.project_name
  organization_id   = var.supabase_organization_id
  database_password = var.supabase_db_password
  region            = "us-east-1"
  plan              = "free"
}

# Apply database migrations after project is created
resource "terraform_data" "db_migration" {
  depends_on = [supabase_project.main]

  provisioner "local-exec" {
    command = "supabase link --project-ref ${supabase_project.main.id} && supabase db push"
  }
}
