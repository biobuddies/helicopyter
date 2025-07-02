# shellcheck shell=bash

# TODO alternate implementation using /proc/$$/cmdline for minimal Docker images
# need to keep something like this for MacOS though
shell=$(ps -p $$ -o 'comm=')
[[ $shell == *bash ]] || cat <<EOD
WARNING: includes.bash has only been tested with, and linted for, BASH. You are running $shell.
Testing multiple shells is a lot of work, and shellcheck does not support zsh.
Run \`chsh -s /bin/bash\` or \`forceready\` to switch.
EOD

set -o vi

BASH_MAJOR_VERSION=$(echo "$BASH_VERSION" | sed -E 's/^([^.]+).+/\1/')

OPSY=$(uname -s)
export OPSY

# Terraform documentation mentions ~/.terraform.d/plugin-cache but prioritizing
# similarity to pre-commit and uv instead.
TF_PLUGIN_CACHE_DIR=~/.cache/terraform
export TF_PLUGIN_CACHE_DIR
mkdir -p "$TF_PLUGIN_CACHE_DIR"

case $OPSY in
    Darwin)
        # Apple stopped upgrading BASH, perhaps to avoid GPLv3, and switched to ZSH.
        # https://apple.stackexchange.com/q/371997
        # See devready and forceready for upgrading BASH with Brew.
        [[ $BASH_MAJOR_VERSION -gt 3 ]] || export BASH_SILENCE_DEPRECATION_WARNING=1

        # Pre-installed on Sonoma:
        #   * Skip upgrades: host, file, less, ps
        #   * Upgrade: bash, curl, git (may come with xcode)
        BRWS='asdf bash curl fping git gnu-sed tmux tree'
        export BRWS

        # https://github.com/ansible/ansible/issues/32499
        export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
        [[ ! -x /opt/homebrew/bin/brew ]] || eval "$(/opt/homebrew/bin/brew shellenv)"
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

if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    PATH="$HOME/.local/bin:$PATH"
fi

PATH="$HOME/.asdf/shims:$PATH"
export PATH
if [[ $(command -v asdf) ]]; then
    # shellcheck disable=SC1090
    source <(asdf completion bash)
    # If this spews "Unknown command: `asdf completion bash`", upgrade asdf
fi

CLICOLOR_FORCE=1 # For `tree`; might also color `ls` on FreeBSD and Darwin
export CLICOLOR_FORCE

# F: no-op for single page, R: color, X: keep text when exiting, i: case insensitive searching
LESS='-FRXi'
export LESS

ASDF_PLUGINS='nodejs tenv uv'
export ASDF_PLUGINS

# Defined for all operating systems to support Linux containers from MacOS
DEBS='bash bind9-host curl file fping git less procps tmux tree'
export DEBS

# We should probably deprecate `PACKAGES` in favor of `DEBS` and `BRWS`.
PACKAGES="$DEBS"
export PACKAGES

# Aliases only work in interactive shells
alias grep='grep --color=auto'
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
        source ~/miniconda3/etc/profile.d/conda.sh
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

expected_git_configuration="
advice.skippedCherryPicks=false Reduces noise when pull requests are squashed on the server side
core.commentChar=; Allows # hash character to be used for Markdown headers
diff.colormoved=zebra Distinguishes moved lines from added and removed lines
init.defaultBranch=main New standard value skips long explanation
pull.rebase=true Always be rebasing
push.default=current Use feature branches with \"GitHub Flow\"
rebase.autosquash=true Act on \"fixup\!\" and \"squash\!\" commit title prefixes
user.email=${INSH_EMAIL:-\$INSH_EMAIL} Inconsistency breaks reports like git shortlog
user.name=${INSH_NAME:-\$INSH_NAME} Inconsistency breaks reports like git shortlog
"

devready() {
    : 'DEVelopment READYness check'
    if [[ $(command -v asdf) ]]; then
        grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
            || echo 'TODO: legacy_version_file = yes
Files like .python-version will be ignored'
        local installed_asdf_plugins
        installed_asdf_plugins=$(asdf plugin list 2>/dev/null)
        for plugin in $ASDF_PLUGINS; do
            if [[ $installed_asdf_plugins != *$plugin* ]]; then
                echo "TODO: asdf plugin add $plugin"
            fi
        done
    else
        echo 'TODO: install asdf
asdf is a version manager for node, tenv (terraform, tofu), uv (python), and more'
    fi

    for line in $(
        comm -13i <(git config --global --list | sort) <(echo "$expected_git_configuration" | cut -f 1 -d ' ')
    ); do
        identifier=${line/=/}
        echo -n "TODO: git config --global "
        echo "$expected_git_configuration" | sed -n /${line/=*/}/'{s/=/ /; p;}'
    done

    if [[ $OPSY == Darwin ]]; then
        if [[ $(command -v brew) ]]; then
            installed_brews="$(brew list)"
            for brew in $BRWS; do
                if [[ $installed_brews != *$brew* ]]; then
                    echo "TODO: brew install $brew"
                fi
            done
        else
            echo ERROR: Homebrew not installed
        fi
        [[ $BASH_MAJOR_VERSION -gt 3 ]] \
            || echo "TODO: Upgrade bash beyond $BASH_VERSION"
        grep --fixed-strings --no-messages --quiet .DS_Store ~/.config/git/ignore \
            || echo TODO: git ignore .DS_Store files 
        [[ $(defaults read NSGlobalDomain ApplePressAndHoldEnabled) == '0' ]] \
            || echo TODO: Turn off MacOS press and hold
        [[ $(defaults read NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled) == '0' ]] \
            || echo TODO: Turn off MacOS period substitution
        [[ $(defaults read NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled) == '0' ]] \
            || echo TODO: Trun off MacOS quote substitution
    elif [[ $OPSY == Linux ]]; then
        [[ $USER == root ]] || $(type -p sudo >/dev/null) \
            || echo ERROR: USER=$USER and sudo missing
        installed_debs="$(dpkg-query -W --showformat='${Package}\n')"
        for deb in $DEBS; do
            if [[ $installed_debs != *$deb* ]]; then
                echo "TODO: apt-get install $deb"
            fi
        done
    else
        echo "ERROR: Unsupported operating system $OPSY"
    fi
}

ups() {
    : 'Uv venv and Pip Sync and similar for npm'
    [[ ! -f package-lock.json ]] || npm install --frozen-lockfile
    [[ -f requirements.txt ]] || return
    uv venv && uv pip sync "$@" requirements.txt
}

asdf_url=https://github.com/asdf-vm/asdf/releases/download/v0.16.7/asdf-v0.16.7-linux-amd64.tar.gz

forceready() {
    : 'FORCE system to be READY for development, clobbering current settings'
    if [[ $shell != *bash ]]; then
        chsh -s /bin/bash
        echo 'Shell changed to BASH. Please restart your shell and rerun forceready.'
        # TODO could we run this function with bash?
        return
    fi

    for directory in .config/git .local/bin code; do
        [[ -d ~/$directory ]] || mkdir -p ~/$directory
    done
    [[ -z $GITHUB_WORKSPACE ]] || ln -s "$GITHUB_WORKSPACE" ~/code/

    if [[ $OPSY == Darwin ]]; then
        # Should we set NONINTERACTIVE=1 ?
        [[ $(command -v brew) ]] || /bin/bash -c "$(
            curl --fail --show-error --silent \
                https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh
        )"
        eval "$(/opt/homebrew/bin/brew shellenv)"
        # shellcheck disable=SC2086
        [[ -z ${BRWS-} ]] || brew install --quiet $BRWS
        [[ -f ~/.config/git/ignore ]] || curl --fail --show-error --silent --output ~/.config/git/ignore \
            https://raw.githubusercontent.com/github/gitignore/master/Global/macOS.gitignore
        defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
    elif [[ $OPSY == Linux ]]; then
        if [[ ${DEBS-} ]]; then
            if [[ $USER == root ]]; then
                apt-get update
                # shellcheck disable=SC2046,SC2086
                apt-get install --no-install-recommends --yes $DEBS
            elif $(type -p sudo >/dev/null); then
                sudo apt-get update
                # shellcheck disable=SC2046,SC2086
                sudo apt-get install --no-install-recommends --yes $DEBS
            else
                echo ERROR: USER=$USER and sudo missing
                return 1
            fi
        fi
        [[ -x ~/.local/bin/asdf ]] || curl --fail --location --show-error --silent $asdf_url \
            | tar -xzC ~/.local/bin
        if ! asdf --version >/dev/null; then
            echo ERROR: asdf installation failed
            echo "PATH=$PATH"
            return 1
        fi
    fi

    grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
        || echo 'legacy_version_file = yes' >>~/.asdfrc
    local installed_asdf_plugins
    installed_asdf_plugins=$(asdf plugin list 2>/dev/null)
    for plugin in $ASDF_PLUGINS; do
        [[ $installed_asdf_plugins == *$plugin* ]] \
            || asdf plugin add "$plugin" "$(
                echo "$plugin" | sed -n s,tenv,https://github.com/tofuutils/asdf-tenv,p
            )"
        asdf install "$plugin"
    done
    # TODO set TENV_GITHUB_TOKEN to avoid rate limiting
    ! [[ -f .terraform-version ]] || tenv terraform install
    ! [[ -f .tofu-version ]] || tenv opentofu install

    eval $(
        echo "$expected_git_configuration" \
            | sed -E '/\$/d; s/^([^=]+)=([^ ]+).*/git config --global \1 "\2"; /'
    )
    [[ ${INSH_NAME-} || ${GITHUB_WORKSPACE-} || $USER == root ]] \
        || echo 'WARNING: Not setting git user.name. Run:
export INSH_NAME="Your Name"; forceready'
    [[ ${INSH_EMAIL-} || ${GITHUB_WORKSPACE-} || $USER == root ]] \
        || echo 'WARNING: Not setting git user.email. Run:
export INSH_EMAIL=youremail@yourdomain.tld; forceready'

    asdf current
    # might be nice to show tofu, python, terraform, versions like calling pathver

    ups "$@"
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
    : 'list FUNCTIONS defined by .biobuddies/includes.bash'
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
    ${INSH_TF:-terraform} -chdir="deploys/$cona/terraform" init "$@"
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
        # git will have colon :, https will have slash /
        git remote get-url origin | sed -E 's,.+github.com[:/]([^/]+).+,\1,'
    fi
}

pc() {
    : 'run Pre-Commit on modified files'
    pre-commit run "$@"
}

pca() {
    : 'run Pre-Commit on All files'
    if [[ $(cona) == helicopyter ]]; then
        command=try-repo
    else
        command=run
    fi
    pre-commit $command --all-files "$@"
}

pcam() {
    : 'run Pre-Commit on All files including Manual stage hooks'
    pre-commit run --all-files --hook-stage manual "$@"
}

pcm() {
    : 'run Pre-Commit on modified files including Manual stage hooks'
    pre-commit run --hook-stage manual "$@"
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
