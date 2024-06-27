"""Configure GitHub repositories."""

from cdktf_cdktf_provider_github.repository import Repository

from helicopyter import HeliStack

repositories = {
    'airdjang': ('Airflow + Django', ['airflow', 'django', 'python']),
    'allowedflare': ('Intranet connectivity for Django and more', ['django', 'python']),
    'helicopyter': ('Python-defined infrastructure', ['ansible', 'cdktf', 'python', 'terraform']),
}


def synth(stack: HeliStack) -> None:
    stack.provide('github')

    for name, (description, topics) in repositories.items():
        stack.push(
            Repository,
            name,
            import_id=name,
            allow_auto_merge=True,
            allow_merge_commit=False,
            allow_rebase_merge=True,
            allow_squash_merge=True,
            allow_update_branch=True,
            delete_branch_on_merge=True,
            description=description,
            has_downloads=False,
            has_issues=True,
            has_projects=False,
            has_wiki=False,
            name=name,
            # Merge commits aren't expected but just in case
            merge_commit_message='PR_BODY',
            merge_commit_title='PR_TITLE',
            # This might be the most important setting: it copies the the body (top comment) of the
            # Pull Request (PR) on github.com into the git commit message. The default is to list
            # the commit titles which are often much less helpful:
            # "add feature; fix test; really fix test; satisfy linter"
            squash_merge_commit_message='PR_BODY',
            squash_merge_commit_title='PR_TITLE',
            topics=topics,
        )
