terraform {
  required_version = ">= 1.6.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.39"
    }
  }

  # State ni DO Spaces da saqlash (tavsiya etiladi)
  # backend "s3" {
  #   endpoint                    = "https://fra1.digitaloceanspaces.com"
  #   bucket                      = "educrm-tfstate"
  #   key                         = "terraform.tfstate"
  #   region                      = "us-east-1"
  #   skip_credentials_validation = true
  #   skip_metadata_api_check     = true
  #   skip_region_validation      = true
  #   force_path_style            = true
  # }
}

provider "digitalocean" {
  token = var.do_token
}

# Mavjud SSH key
data "digitalocean_ssh_key" "admin" {
  name = var.ssh_key_name
}
