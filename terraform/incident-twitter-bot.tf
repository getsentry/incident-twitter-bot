module "incident-twitter-bot" {
  source              = "../modules/cloud-function-gen2"
  name                = "incident-twitter-bot"
  description         = "Posting updates from https://status.sentry.io to the Sentry Support Twitter account"
  source_dir          = "incident-twitter-bot"
  execution_timeout   = 120
  available_memory_mb = "128Mi"

  secret_environment_variables = [
    {
      key     = "getsentryhelp_twitter_consumer_key"
      secret  = google_secret_manager_secret.secret["getsentryhelp_twitter_consumer_key"].secret_id
      version = "latest"
    },
    {
      key     = "getsentryhelp_twitter_consumer_secret"
      secret  = google_secret_manager_secret.secret["getsentryhelp_twitter_consumer_secret"].secret_id
      version = "latest"
    },
    {
      key     = "getsentryhelp_twitter_access_token"
      secret  = google_secret_manager_secret.secret["getsentryhelp_twitter_access_token"].secret_id
      version = "latest"
    },
    {
      key     = "getsentryhelp_twitter_access_token_secret"
      secret  = google_secret_manager_secret.secret["getsentryhelp_twitter_access_token_secret"].secret_id
      version = "latest"
    }
  ]
}