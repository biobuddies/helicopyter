"""Simple demonstration of a Python-syntax Ansible playbook."""

playbook = [{'hosts': 'localhost', 'gather_facts': 'no', 'tasks': [{'debug': None}]}]
