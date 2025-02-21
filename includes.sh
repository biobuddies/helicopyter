# shellcheck shell=bash

shell=$(ps -p $$ -o 'comm=')
[[ $shell == *bash ]] || cat <<EOD
WARNING: includes.sh has only been tested with, and linted for, BASH. You are running $shell.
Testing multiple shells is a lot of work, and shellcheck does not support zsh.
Run \`chsh -s /bin/bash\` or \`forceready\` to switch.
EOD

set -o vi

OS=$(uname -s)
export OS

case $OS in
    Darwin)
        export BASH_SILENCE_DEPRECATION_WARNING=1
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

# Accept any kind of installation, such as Homebrew
if ! [[ $(command -v asdf) ]]; then
    if [[ -f $HOME/code/asdf/asdf.sh ]]; then
        # Automate git installation configuration for old and new paths
        for suffix in asdf.sh completions/asdf.bash internal/completions/asdf.bash; do
            if [[ -f $HOME/code/asdf/$suffix ]]; then
                # shellcheck disable=SC1090,SC1091
                source "$HOME/code/asdf/$suffix"
            fi
        done
    else
        # Recommend git installation
        echo "Please run
git clone https://github.com/asdf-vm/asdf.git ~/code/asdf"
    fi
fi

CLICOLOR_FORCE=1 # For `tree`; might also color `ls` on FreeBSD and Darwin
export CLICOLOR_FORCE

# F: no-op for single page, R: color, X: keep text when exiting, i: case insensitive searching
LESS='-FRXi'
export LESS

PACKAGES='bind9-host curl fping git less tmux tree'
export PACKAGES

# Aliases only work in interactive shells
alias jq='jq --color-output'
alias ls='ls --color=auto'

# Function naming philosophy:
# * Few characters (usually an abbreviation) if frequently typed
# * Descriptive snake_case, just like PEP8, for everything else

pathver() {
    : 'print PATH and VERsion; optionally assert version file matches'
    source=$(type -p "$1")
    if [[ -z $source ]]; then
        source=$(type "$1")
    fi
    actual_version=$("$1" --version 2>&1 | gsed -En 's/(.+ )?(v?[0-9]+\.[0-9]+\.[^ ]+).*/\2/p')
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

    if [[ ${1-} ]]; then
        directory=~/code/$1
    else
        directory=.
    fi

    if ! [[ -d $directory ]]; then
        echo "ERROR: $directory is not a directory"
        return 1
    fi

    cd "$directory" || return 1

    [[ ${CONDA_PREFIX-} && $(command -v conda) ]] && conda deactivate
    if [[ ${VIRTUAL_ENV-} ]]; then
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
        pathver node .nvmrc
    fi
}

build_twine() {
    : 'clean, BUILD, and upload python package with TWINE'
    if [[ $(git describe --exact --tags) != v20* ]]; then
        echo 'ERROR: Please tag in the gvcount or yucount format'
        return 1
    fi
    if [[ $TWINE_USERNAME != '__token__' || -z $TWINE_PASSWORD ]]; then
        echo 'ERROR: Please set TWINE_USERNAME=__token__ and TWINE_PASSWORD=...'
        return 1
    fi
    [[ -d dist ]] || mkdir dist
    rm -r dist && python -m build && twine upload dist/*
}

cona() {
    : 'print CodeNAme, a four letter acronym'
    if [[ ${GITHUB_REPOSITORY-} ]]; then
        echo "${GITHUB_REPOSITORY##*/}"
    elif [[ ${VIRTUAL_ENV-} ]]; then
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

dcp() {
    : 'Docker Compose Push'
    docker compose push --quiet "$@"
}

dcr() {
    : 'Docker Compose Run, respecting docker-compose.yaml port definitions'
    docker compose run --quiet-pull --service-ports "$@"
}

dcs() {
    : 'Docker Compose Shell'
    docker compose run "$(cona)" bash "$@"
}

dcu() {
    : 'Docker Compose Up'
    docker compose up "$@"
}

devready() {
    : 'DEVelopment READYness check'
    grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
        || echo 'WARNING: legacy_version_file != yes
Files like .python-version will be ignored'
    local installed
    installed=$(asdf plugin list 2>/dev/null)
    [[ $installed == *nodejs* ]] \
        || echo 'WARNING: nodejs plugin for asdf not added'
    [[ $installed == *tenv* ]] \
        || echo 'WARNING: tenv plugin for asdf not added'
    [[ $installed == *uv* ]] \
        || echo 'WARNING: uv plugin for asdf not added'

    [[ $(git config --global advice.skippedCherryPicks) == false ]] \
        || echo 'WARNING: git advice.skippedCherryPicks != false
This reduces noise when pull requests are squashed on the server side'
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

    grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
        || echo 'legacy_version_file = yes' >>~/.asdfrc
    local installed
    installed=$(asdf plugin list 2>/dev/null)
    [[ $installed == *nodejs* ]] || asdf plugin add nodejs
    [[ $installed == *tenv* ]] \
        || asdf plugin add tenv https://github.com/tofuutils/asdf-tenv
    [[ $installed == *uv* ]] || asdf plugin add uv

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

envi() {
    : 'print ENVIronment, a four letter acronym'
    if [[ ${ENVI-} ]]; then
        echo "$ENVI"
    elif [[ ${GITHUB_ACTIONS-} ]]; then
        echo github
    else
        echo local
    fi
}

functions() {
    : 'list FUNCTIONS defined by includes.sh'
    gsed -En 's/^ *([^(]+)\(\) \{$/\1/; T; N; s/\n +: /\t\t/; p' "${BASH_SOURCE[0]}"
    echo -e "\nRun \`type function_name\` to display details.\n"
    echo Environment Variables
    echo -e "INSH_TRACE\t\tSet to 'off' to skip \`set -x\`"
    echo -e "INSH_NAME\t\tgit user.name"
    echo -e "INSH_EMAIL\t\tgit user.email"
    echo -e "INSH_RELEASE_PREFIX\tSet to '-%G.%V.' for ISO year and week. Default is '-%Y.%U.'"
    echo -e "INSH_TF\t\t\tSet to 'tofu' where appropriate. Default is 'terraform'"
}

giha() {
    : 'print GIt HAsh, a four letter acronym'
    git describe --abbrev=40 --always --dirty --match=-
}

gash() {
    : 'backwards compatibility wrapper around giha'
    giha
}

hs() {
    : 'Helicopyter Synth'
    local cona="${1:-all}"
    python -m helicopyter --format_with="${INSH_TF:-terraform}" "$cona"
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
    hs "$cona" \
        && TF_VAR_giha=$(giha) TF_VAR_tabr=$(tabr) TF_WORKSPACE="$envi" \
            ${INSH_TF:-terraform} -chdir="deploys/$cona/terraform" apply "$@"
}

hti() {
    : 'Helper for Terraform Init and synth'
    local cona="${1?:Please provide a code name as the first argument}"
    shift
    ${INSH_TF:-terraform} -chdir="deploys/$cona/terraform" init "$@" \
        && hs "$cona"
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
    hs "$cona" \
        && TF_VAR_giha=$(giha) TF_VAR_tabr=$(tabr) TF_WORKSPACE="$envi" \
            ${INSH_TF:-terraform} -chdir="deploys/$cona/terraform" plan "$@"
}

orgn() {
    : 'print ORGanizatioN, a four letter acronym'
    if [[ ${GITHUB_REPOSITORY_OWNER-} ]]; then
        echo "$GITHUB_REPOSITORY_OWNER"
    else
        git remote get-url origin | gsed -E 's,.+github.com/([^/]+).+,\1,'
    fi
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

release() {
    : 'create a github RELEASE, and optionally also run build and twine upload'
    local prefix
    prefix=$(date -u "+v${INSH_RELEASE_PREFIX:-%Y.%U.}")
    git fetch --tags
    local count
    count=$(git tag --list "$prefix*" | gsed "s/$prefix//" | sort -r | head -1)
    gh release create "$prefix$(printf '%02d' $((${count:-0} + 1)))" --generate-notes
    git fetch --tags
    [[ $* == build ]] && build_twine
}

summarize() {
    : 'SUMMARIZE environment by setting and displaying four letter acronyms'
    CONA=$(cona)
    ENVI=$(envi)
    GIHA=$(giha)
    ORGN=$(orgn)
    ROLE="${ROLE-}"
    TABR=$(tabr)
    cat <<EOD | tee "${GITHUB_STEP_SUMMARY:-/dev/null}"
| Unabbreviat. | FLAN | Value                                          |
| ------------ | ---- | ---------------------------------------------- |
| COdeNAme     | CONA | $CONA |
| ENVIronment  | ENVI | $ENVI |
| GIt HAsH     | GIHA | $GIHA |
| ORGanizatioN | ORGN | $ORGN |
| ROLE         | ROLE | $ROLE |
| TAg/BRanch   | TABR | $TABR |
EOD
    if [[ $GITHUB_ENV ]]; then
        # For use by later steps
        cat <<EOD | tee -a "$GITHUB_ENV"
CONA=$CONA
ENVI=$ENVI
GIHA=$GIHA
ORGN=$ORGN
ROLE=$ROLE
TABR=$TABR
EOD
        # For use during this step
        set -o allexport
        # shellcheck disable=SC1090
        source "$GITHUB_ENV"
    fi
}

# Backwards compatibility with GitHub Actions Summary abbreviation
ghas() { summarize; }

tabr() {
    : 'print TAg or BRanch or empty string, a four letter acronym'
    # GITHUB_HEAD_REF works for Pull Requests, GITHUB_REF_NAME for all the other triggers
    # https://stackoverflow.com/questions/58033366
    # In contrast to the git metadata, the GitHub Actions environment variables are available before
    # git checkout, and may be less ambiguous.
    if [[ ${GITHUB_HEAD_REF-} ]]; then
        echo "$GITHUB_HEAD_REF"
    elif [[ ${GITHUB_REF_NAME-} ]]; then
        echo "$GITHUB_REF_NAME"
    else
        # remotes/origin/mybranch -> mybranch
        # heads/mybranch -> mybranch
        # tags/v2025.02.03 -> v2025.02.03
        # heads/mybranch-dirty -> '' #empty string
        git describe --all --dirty --exact-match 2>/dev/null \
            | gsed -En '/-dirty$/ q; s,(remotes/[^/]+|heads|tags)/,,p'
    fi
}

upc() {
    : 'Uv Pip Compile'
    # shellcheck disable=SC2046
    uv pip compile \
        --all-extras \
        --output-file requirements.txt \
        --python-platform linux \
        pyproject.toml $([[ -f requirements.in ]] && echo requirements.in)
}

ups() {
    : 'Uv Pip Sync, with MacOS workaround for appnope'
    uv pip sync "$@" requirements.txt
}

uuid() {
    : 'Universally Unique IDentifier'
    python -c 'import uuid; print(uuid.uuid4())'
}

if [[ $* ]]; then
    if [[ ${INSH_TRACE-} == 'off' ]]; then
        "$@"
    else
        (
            set -x
            "$@"
        )
    fi
fi
