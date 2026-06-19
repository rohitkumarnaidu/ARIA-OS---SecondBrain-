resource "vercel_project" "frontend" {
  name           = "${var.project_name}-web"
  framework      = "nextjs"
  root_directory = "apps/web"

  git_repository = {
    type = "github"
    repo = "username/second-brain-os"
  }

  environment = [
    {
      key    = "NEXT_PUBLIC_SUPABASE_URL"
      value  = supabase_project.main.api_url
      target = ["production", "preview"]
    },
    {
      key    = "NEXT_PUBLIC_SUPABASE_ANON_KEY"
      value  = supabase_project.main.anon_key
      target = ["production", "preview"]
    }
  ]
}

resource "vercel_project" "backend" {
  name           = "${var.project_name}-api"
  framework      = "other"
  root_directory = "apps/api"

  git_repository = {
    type = "github"
    repo = "username/second-brain-os"
  }

  environment = [
    {
      key    = "SUPABASE_URL"
      value  = supabase_project.main.api_url
      target = ["production", "preview"]
    },
    {
      key    = "SUPABASE_SERVICE_KEY"
      value  = supabase_project.main.service_role_key
      target = ["production", "preview"]
    }
  ]
}
