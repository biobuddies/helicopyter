# Helicopyter

Like a helicopter hovering between the clouds and the ground, Helicopyter allows people to describe infrastructure using Python in a way that's less like the AWS Cloud Development Kit (CDK) and more like Terraform.

It is inspired by [Configerator](https://research.facebook.com/file/877841159827226/holistic-configuration-management-at-facebook.pdf), [Terraformpy](https://github.com/NerdWalletOSS/terraformpy), [Terraform JSON configuration syntax](https://developer.hashicorp.com/terraform/language/syntax/json), and uses [CDKTF](https://github.com/hashicorp/terraform-cdk).

Terraform has a pretty good command line interface, so Helicopyter focuses on generating JSON it can easily use.

Meaningful names make review easy. Terraform's resource prefix style results in meaningful names and aligns with "Namespaces are one honking great idea -- let's do more of those!" The AWS CDK style of suffixing hashes does neither.

Possible future directions:
- [ ] The f'deploys/{deploy}/terraform' directory structure may be surprising. What's a better layout that allows the Terraform to coexist nicely with other tools like Ansible and Python scripts?
- [ ] `id` is a built-in function, and given special highlighting in vim, so rename the argument to something like `name`
- [ ] `__str__()` for `to_string()`, etc.
- [ ] Why do we need a Node.js server? If CDKTF is able to generate this much Python, why not just generate dataclasses or Pydantic models?
