terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "6.17.0"
    }
  }
}

provider "google" {
  credentials = "./keys/my-key.json"
  project = "terraform-project-449109"
  region  = "us-central1"
}

resource "google_storage_bucket" "demo-bucket" {
  name          = "terraform-project-449109-my-terra-bucket"
  location      = "US"
  force_destroy = true

  # Optional, but recommended settings:
  storage_class = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled     = true
  }  

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "dataset_project_zoomcamp" {
  dataset_id = "dataset_zoomcamp"
  project    = "terraform-project-449109"
  location   = "US"
}