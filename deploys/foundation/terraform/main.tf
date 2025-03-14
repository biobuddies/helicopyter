# AUTOGENERATED by helicopyter

import {
  to = github_repository.airdjang
  id = "airdjang"
}

import {
  to = github_repository.allowedflare
  id = "allowedflare"
}

import {
  to = github_repository.helicopyter
  id = "helicopyter"
}

import {
  to = github_repository.wellplated
  id = "wellplated"
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
    key                         = "foundation.tfstate"
    region                      = "auto"
    workspace_key_prefix        = "foundation"
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

resource "github_repository" "airdjang" {
  allow_auto_merge            = true
  allow_merge_commit          = false
  allow_rebase_merge          = true
  allow_squash_merge          = true
  allow_update_branch         = true
  delete_branch_on_merge      = true
  description                 = "Airflow + Django"
  has_downloads               = false
  has_issues                  = true
  has_projects                = false
  has_wiki                    = false
  merge_commit_message        = "PR_BODY"
  merge_commit_title          = "PR_TITLE"
  name                        = "airdjang"
  squash_merge_commit_message = "PR_BODY"
  squash_merge_commit_title   = "PR_TITLE"
  topics = [
    "airflow",
    "django",
    "python"
  ]
}

resource "github_repository" "allowedflare" {
  allow_auto_merge            = true
  allow_merge_commit          = false
  allow_rebase_merge          = true
  allow_squash_merge          = true
  allow_update_branch         = true
  delete_branch_on_merge      = true
  description                 = "Intranet connectivity for Django and more"
  has_downloads               = false
  has_issues                  = true
  has_projects                = false
  has_wiki                    = false
  merge_commit_message        = "PR_BODY"
  merge_commit_title          = "PR_TITLE"
  name                        = "allowedflare"
  squash_merge_commit_message = "PR_BODY"
  squash_merge_commit_title   = "PR_TITLE"
  topics = [
    "django",
    "python"
  ]
}

resource "github_repository" "helicopyter" {
  allow_auto_merge            = true
  allow_merge_commit          = false
  allow_rebase_merge          = true
  allow_squash_merge          = true
  allow_update_branch         = true
  delete_branch_on_merge      = true
  description                 = "Python-defined infrastructure"
  has_downloads               = false
  has_issues                  = true
  has_projects                = false
  has_wiki                    = false
  merge_commit_message        = "PR_BODY"
  merge_commit_title          = "PR_TITLE"
  name                        = "helicopyter"
  squash_merge_commit_message = "PR_BODY"
  squash_merge_commit_title   = "PR_TITLE"
  topics = [
    "ansible",
    "cdktf",
    "python",
    "terraform"
  ]
}

resource "github_repository" "wellplated" {
  allow_auto_merge            = true
  allow_merge_commit          = false
  allow_rebase_merge          = true
  allow_squash_merge          = true
  allow_update_branch         = true
  delete_branch_on_merge      = true
  description                 = "Python Django models for liquid handling"
  has_downloads               = false
  has_issues                  = true
  has_projects                = false
  has_wiki                    = false
  merge_commit_message        = "PR_BODY"
  merge_commit_title          = "PR_TITLE"
  name                        = "wellplated"
  squash_merge_commit_message = "PR_BODY"
  squash_merge_commit_title   = "PR_TITLE"
  topics = [
    "django",
    "python"
  ]
}
