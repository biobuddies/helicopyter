"""Configure GitHub repositories."""

from helicopyter import cona, provider, resource, terraform
from stacks.base import r2_backend

repositories = {
    'airdjang': ('Airflow + Django', ['airflow', 'django', 'python']),
    'allowedflare': ('Intranet connectivity for Django and more', ['django', 'python']),
    'helicopyter': ('Python-defined infrastructure', ['ansible', 'cdktf', 'python', 'terraform']),
    'measles': ('Continuous cookiecutter featuring mise', ['cookiecutter', 'python']),
    'wellplated': ('Python Django models for liquid handling', ['django', 'python']),
}

r2_backend(cona, terraform)
terraform.required_providers(
    github={'source': 'integrations/github', 'version': '>=6.6.0'},
)
provider.github(owner='biobuddies')

for name, (description, topics) in repositories.items():
    resource.github_repository(name)(
        allow_auto_merge=True,
        allow_merge_commit=False,
        allow_rebase_merge=True,
        allow_squash_merge=True,
        allow_update_branch=True,
        delete_branch_on_merge=True,
        description=description,
        has_issues=True,
        has_projects=False,
        has_wiki=False,
        # Merge commits aren't expected but just in case
        merge_commit_message='PR_BODY',
        merge_commit_title='PR_TITLE',
        name=name,
        # This might be the most important setting: it copies the the body (top comment) of the
        # Pull Request (PR) on github.com into the git commit message. The default is to list
        # the commit titles which are often much less helpful:
        # "add feature; fix test; really fix test; satisfy linter"
        squash_merge_commit_message='PR_BODY',
        squash_merge_commit_title='PR_TITLE',
        topics=topics,
    )
