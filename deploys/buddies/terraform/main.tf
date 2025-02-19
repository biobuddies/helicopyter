# AUTOGENERATED by helicopyter

import {
  to = github_membership.christopher_covington
  id = "biobuddies:covracer"
}

import {
  to = github_membership.darren_pham
  id = "biobuddies:darpham"
}

import {
  to = github_membership.duncan_tormey
  id = "biobuddies:DuncanTormey"
}

import {
  to = github_membership.james_braza
  id = "biobuddies:jamesbraza"
}

import {
  to = github_membership.matt_fowler
  id = "biobuddies:mattefowler"
}

import {
  to = github_membership.nadia_wallace
  id = "biobuddies:16NWallace"
}

terraform {
  required_providers {
    github = {
      version = "6.5.0"
      source  = "integrations/github"
    }
  }
  backend "s3" {
    bucket                      = "terraform"
    key                         = "buddies.tfstate"
    region                      = "auto"
    workspace_key_prefix        = "buddies"
    skip_credentials_validation = "true"
    skip_metadata_api_check     = "true"
    skip_region_validation      = "true"
    skip_requesting_account_id  = "true"
    skip_s3_checksum            = "true"
    use_path_style              = "true"
  }
}

provider "github" {
  owner = "biobuddies"
}

resource "github_membership" "christopher_covington" {
  role     = "admin"
  username = "covracer"
}

resource "github_membership" "darren_pham" {
  role     = "admin"
  username = "darpham"
}

resource "github_membership" "duncan_tormey" {
  role     = "admin"
  username = "DuncanTormey"
}

resource "github_membership" "james_braza" {
  role     = "admin"
  username = "jamesbraza"
}

resource "github_membership" "matt_fowler" {
  role     = "admin"
  username = "mattefowler"
}

resource "github_membership" "nadia_wallace" {
  role     = "admin"
  username = "16NWallace"
}
