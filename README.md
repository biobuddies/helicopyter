# Helicopyter

Helicopyter allows people to conveniently describe infrastructure using Python.

Perhaps like a helicopter hovering between the clouds and the ground, it allows this in a way that's less like the AWS
Cloud Development Kit (CDK) and more like Terraform.

## Background
Helicopyter uses [CDKTF](https://github.com/hashicorp/terraform-cdk) and is inspired by [Configerator](https://research.facebook.com/file/877841159827226/holistic-configuration-management-at-facebook.pdf), [Terraformpy](https://github.com/NerdWalletOSS/terraformpy), and [Terraform JSON configuration syntax](https://developer.hashicorp.com/terraform/language/syntax/json).

## What Helicopyter does (goals)
- Fix the CDKTF naming mess. Meaningful names make review easy. Terraform's resource prefix style results in meaningful
  names and aligns with "Namespaces are one honking great idea -- let's do more of those!" The AWS CDK style of
  suffixing hashes generates difficult-to-review `terraform plan` output and ignores the existing namespaces.
- Provide a directory structure that groups primarily by "codename" (could be called application, service) and secondarily by tool. For now it assumes f'deploys/{codename}/terraform'.

## What Helicopyter will probably never do (non-goals)
- Terraform has a pretty good command line interface. Helicopyter focuses on generating JSON for it. Helicopyter does
  not try to wrap the `terraform` command line interface itself and using CDKTF's wrapper is untested and not
  recommended.

## What Helicopyter might do in the future
- Support multiple backend configurations per codename
- Iterate on the directory structure
- `__str__()` for `to_string()`, etc.
- Why do we need a Node.js server? Can we build dataclasses or Pydantic models out of the type annotations already being
  generated?
