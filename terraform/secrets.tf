resource "google_secret_manager_secret" "secret" {
  for_each  = { for s in local.secrets : s => s }
  secret_id = each.value
  replication {
    auto {}
  }
}

locals {
  secrets = [
    "getsentryhelp_twitter_consumer_key",
    "getsentryhelp_twitter_consumer_secret",
    "getsentryhelp_twitter_access_token",
    "getsentryhelp_twitter_access_token_secret",
  ]
}