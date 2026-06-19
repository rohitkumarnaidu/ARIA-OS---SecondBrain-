output "supabase_project_id" {
  value       = supabase_project.main.id
  description = "Supabase project ID"
}

output "supabase_api_url" {
  value       = supabase_project.main.api_url
  description = "Supabase API URL"
  sensitive   = true
}

output "supabase_anon_key" {
  value       = supabase_project.main.anon_key
  description = "Supabase anonymous key"
  sensitive   = true
}

output "vercel_frontend_url" {
  value       = vercel_project.frontend.domains[0]
  description = "Vercel frontend URL"
}

output "vercel_backend_url" {
  value       = vercel_project.backend.domains[0]
  description = "Vercel backend URL"
}
