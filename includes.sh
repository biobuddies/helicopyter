# shellcheck shell=bash

[[ $BASH ]] || cat <<EOD
WARNING: includes.sh has only been tested with, and linted for, Bash. You are running $0.
Run \`chsh -s /bin/bash\` or \`forceready\` to switch.
EOD

set -o vi

OS=$(uname -s)

case $OS in
    Darwin)
        export BASH_SILENCE_DEPRECATION_WARNING=1

        if ! [[ -x $(command -v brew) ]]; then
            [[ -d /opt/homebrew/bin ]] && export PATH="/opt/homebrew/bin:$PATH"
            [[ -x $(command -v brew) ]] || echo ERROR: homebrew missing
        fi

        ;;
    Linux)
        gsed() {
            : 'Gnu SED'
            sed "$@"
        }
        open() {
            : 'OPEN directory, file, or uniform resource locator'
            xdg-open "$@"
        }
        ;;
esac

if ! [[ -x $(command -v nvm) ]]; then
    NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
    # shellcheck disable=SC1091
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" || echo INFO: nvm missing
fi

# F: no-op for single page, R: color, X: keep text when exiting, i: case insensitive searching
LESS='-FRXi'
export LESS

# Aliases only work in interactive shells
alias jq='jq --color-output'
alias ls='ls --color=auto'

pathver() {
    : 'print PATH and VERsion; optionally assert version file matches'
    source=$(type -p "$1")
    if [[ -z $source ]]; then
        source=$(type "$1")
    fi
    actual_version=$("$1" --version | gsed -E "s/($1 )?//i")
    echo "$source $actual_version"
    if [[ -f $2 ]]; then
        expected_version=$(cat "$2")
        if [[ $actual_version != "$expected_version" ]]; then
            echo "ERROR: $source version $actual_version does not match $2 $expected_version"
            return 1
        fi
    fi
}

a() {
    : 'Activate virtual environment after changing directory'

    if [[ $1 ]]; then
        directory=~/code/$1
    else
        directory=.
    fi

    if ! [[ -d $directory ]]; then
        echo "ERROR: $directory is not a directory"
        return 1
    fi

    cd "$directory" || return 1

    [[ $(command -v conda) ]] && conda deactivate
    might_be_file=$(command -v deactivate)
    if [[ $might_be_file ]]; then
        if [[ -f $might_be_file ]]; then
            # pyenv-virtualenv wants this
            # shellcheck disable=SC1091
            source deactivate
        else
            deactivate
        fi
    fi

    if [[ -f .venv/bin/activate ]]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
        pathver python .python-version
    elif [[ -d conda ]]; then
        # shellcheck disable=SC1091
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate "$(basename "$PWD")"
        pathver python .python-version
    fi

    if [[ -f .nvmrc ]]; then
        nvm install &>/dev/null && nvm use &>/dev/null
        pathver node .nvmrc
    fi

    export PS1='\w$ '
}

cona() {
    : 'CodeNAme'
    if [[ $GITHUB_REPOSITORY ]]; then
        echo "${GITHUB_REPOSITORY##*/}"
    elif [[ $VIRTUAL_ENV ]]; then
        basename "${VIRTUAL_ENV%/.venv}"
    else
        basename "$PWD"
    fi
}

check_mailmap() {
    : 'CHECK for missing MAILMAP entries by surfacing different names for the same email'
    # Could be expanded to optionally require ALLOWEDFLARE_PRIVATE_DOMAIN.
    # Could be expanded to warn about same name, different email.
    local return_code=0
    local emails_names
    emails_names=$(git log --format='%aE	%aN' --use-mailmap | sort --unique)
    for repeat in $(echo "$emails_names" | cut -f 1 | uniq --repeated); do
        echo "$emails_names" | grep "$repeat"
        echo
        return_code=1
    done
    [[ $return_code == 0 ]] || echo 'Multiple names are associated with the same email address.'
    return $return_code
}

dcb() {
    : 'Docker Compose Build'
    docker compose --progress=plain build "$@"
}

dcs() {
    : 'Docker Compose Shell'
    docker compose run "$(cona)" bash "$@"
}

dcr() {
    : 'Docker Compose Run'
    docker compose run "$@"
}

devready() {
    : 'DEVelopment READYness check'
    [[ $0 == *bash ]] || echo 'ERROR: not running in BASH
Testing multiple shells is a lot of work, and shellcheck does not support zsh.'
    [[ $(git config --global advice.skippedCherryPicks) == false ]] \
        || echo 'WARNING: git advice.skippedCherryPicks != false
This reduces noise when pull requests are squashed on the server side.'
    [[ $(git config --global core.commentChar) == ';' ]] \
        || echo 'WARNING: git core.commentChar != ;
This allows # hash character to be used for Markdown headers'
    [[ $(git config --global diff.colormoved) == zebra ]] \
        || echo 'WARNING: git diff.colormoved != zebra
This distinguishes moved lines from added and removed lines'
    [[ $(git config --global user.name) ]] \
        || echo 'ERROR: git user.name missing
Inconsistency breaks reports like git shortlog'
    [[ $(git config --global user.email) ]] \
        || echo 'ERROR: git user.email missing
Inconsistency breaks reports like git shortlog'
    [[ $(git config --global pull.rebase) == true ]] \
        || echo 'WARNING: git pull.rebase != true
Always be rebasing'
    [[ $(git config --global push.default) == current ]] \
        || echo 'WARNING: git push.default != current
Use feature branches with "GitHub Flow"'
    [[ $(git config --global rebase.autosquash) == true ]] \
        || echo 'WARNING: git rebase.autosquash != true
Act on "fixup!" and "squash!" commit title prefixes'
    if [[ $OS == Darwin ]]; then
        grep --fixed-strings --no-messages --quiet .DS_Store ~/.config/git/ignore \
            || echo WARNING: .DS_Store files not globally git ignored
        [[ $(defaults read NSGlobalDomain ApplePressAndHoldEnabled) == '0' ]] \
            || echo WARNING: MacOS press and hold enabled
        [[ $(defaults read NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled) == '0' ]] \
            || echo WARNING: MacOS period substitution enabled
        [[ $(defaults read NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled) == '0' ]] \
            || echo WARNING: MacOS quote substitution enabled
    fi
}

forceready() {
    : 'FORCE system to be READY for development, clobbering current settings'
    if [[ $0 != *bash ]]; then
        chsh -s /bin/bash
        echo 'Shell changed to BASH. Please restart your shell and rerun forceready.'
        # TODO could we run this function with bash?
        return
    fi

    git config --global advice.skippedCherryPicks false
    git config --global core.commentChar ';'
    git config --global diff.colormoved zebra
    ! [[ $INSH_NAME ]] || git config --global user.name "$INSH_NAME"
    ! [[ $INSH_EMAIL ]] || git config --global user.email "$INSH_EMAIL"
    git config --global pull.rebase true
    git config --global push.default current
    git config --global rebase.autosquash true
    [[ -d ~/.config/git ]] || mkdir -p ~/.config/git

    if [[ $OS == Darwin ]]; then
        [[ -f ~/.config/git/ignore ]] || curl -so ~/.config/git/ignore \
            https://raw.githubusercontent.com/github/gitignore/master/Global/macOS.gitignore
        defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
    fi
}

gash() {
    : 'Git hASH'
    git describe --abbrev=40 --always --dirty --match=-
}

hta() {
    : 'Helicopyter synth and Terraform Apply'
    local cona="${1?:Please provide a code name as the first argument}"
    local envi="${2?:Please provide an environment as the second argument}"
    if [[ $envi == default ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        return 1
    fi
    shift 2
    python -m helicopyter "$cona"
    TF_WORKSPACE="$envi" terraform -chdir="deploys/$cona/terraform" apply "$@"
}

hti() {
    : 'Helper for Terraform Init'
    local cona="${1?:Please provide a code name as the first argument}"
    shift
    terraform -chdir="deploys/$cona/terraform" init "$@"
}

htp() {
    : 'Helicopyter synth and Terraform Plan'
    local cona="${1?:Please provide a code name as the first argument}"
    local envi="${2?:Please provide an environment as the second argument}"
    if [[ $envi == default ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        return 1
    fi
    shift 2
    python -m helicopyter "$cona"
    TF_WORKSPACE="$envi" terraform -chdir="deploys/$cona/terraform" plan "$@"
}

pc() {
    : 'run Pre-Commit on modified files'
    pre-commit run "$@"
}

pca() {
    : 'run Pre-Commit on All files'
    pre-commit run --all-files "$@"
}

pcam() {
    : 'run Pre-Commit on All files including Manual stage hooks'
    pre-commit run --all-files --hook-stage manual "$@"
}

pcm() {
    : 'run Pre-Commit on modified files including Manual stage hooks'
    pre-commit run --hook-stage manual "$@"
}

pcta() {
    : 'run Pre-Commit Try-repo on All files'
    pre-commit try-repo \
        --all-files \
        --color always \
        --show-diff-on-failure \
        --verbose \
        . \
        "$@"
}

pctam() {
    : 'run Pre-Commit Try-repo on All files including Manual stage hooks'
    if [[ -z $* ]]; then
        echo 'Please specify a specific hook to run, such as mypy.'
        echo 'The gitignore hooks conflict with each other; includes-sh hook will revert changes.'
        return 1
    fi
    pre-commit try-repo \
        --all-files \
        --color always \
        --hook-stage manual \
        --show-diff-on-failure \
        --verbose \
        . \
        "$@"
}

resourcerun() {
    : 'RE-SOURCE this file and RUN the specified function with tracing enabled'
    # shellcheck source=includes.sh
    source "${BASH_SOURCE[0]}"
    set -x
    "$@"
    set +x
}

summarize() {
    : 'SUMMARIZE for github actions'
    cat <<EOD | tee "${GITHUB_STEP_SUMMARY:-/dev/null}"
| FLAN | Unabbrev.  | Value                                          |
| ---- | ---------- | ---------------------------------------------- |
| CONA | COdeNAme   | $(cona) |
| GASH | Git hASH   | $(gash) |
| TABR | TAg/BRanch | $(tabr) |
EOD
}

# Backwards compatibility with GitHub Actions Summary abbreviation
ghas() { summarize; }

tabr() {
    : 'TAg or BRanch or empty string'
    # GITHUB_HEAD_REF works for Pull Requests, GITHUB_REF_NAME for all the other triggers
    # https://stackoverflow.com/questions/58033366
    echo "${GITHUB_HEAD_REF:-$GITHUB_REF_NAME}"
    # TODO how should people set this locally? `git describe --tags`?
}

ups() {
    : 'Uv Pip Sync'
    uv pip sync requirements.txt "$@"
}

uuid() {
    : 'Universally Unique IDentifier'
    python -c 'import uuid; print(uuid.uuid4())'
}

yucount() {
    : '%Y %U COUNT style version string'
    local yu
    yu=$(date -u +v%Y.%U.)
    git fetch --tags
    local count
    count=$(git tag --list "$yu*" | gsed "s/$yu//" | sort -r | head -1)
    date -u "+v%Y.%U.$((${count:-0} + 1))"
}

if [[ $* ]]; then
    "$@"
fi
