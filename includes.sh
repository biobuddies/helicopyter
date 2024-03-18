# shellcheck shell=bash

OS=$(uname -s)

case $OS in
    Darwin)
        export BASH_SILENCE_DEPRECATION_WARNING=1

        if ! [[ -x $(command -v brew) ]]; then
            [[ -d /opt/homebrew/bin ]] && export PATH="/opt/homebrew/bin:$PATH"
            [[ -x $(command -v brew) ]] || echo ERROR: homebrew missing
        fi

        ;;
esac

if ! [[ -x $(command -v nvm) ]]; then
    NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
    # shellcheck disable=SC1091
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" || echo ERROR: nvm missing
fi

# F: no-op for single page, R: color, X: keep text when exiting, i: case insensitive searching
LESS='-FRXi'
export LESS

# Aliases only work in interactive shells
alias jq='jq --color-output'
alias ls='ls --color=auto'

pathver() {
    : 'Print path and version'
    (type "$1" && "$1" --version) |
        sed -Ee N -e 's,^[^/(]*,,' -e 's,\((.+)\),\1,' -e "s/\n($1 )?/ /i"
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
    [[ $(command -v deactivate) ]] && deactivate
    # TODO pyenv-virtualenv wants `. deactivate`

    if [[ -f .venv/bin/activate ]]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
        pathver python
    elif [[ -d conda ]]; then
        # shellcheck disable=SC1091
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate "$(basename "$PWD")"
        pathver python
    fi

    if [[ -f .nvmrc ]]; then
        nvm install &>/dev/null && nvm use &>/dev/null
        pathver node
    fi

    export PS1='\w$ '
}

devready() {
    : 'DEVelopment READYness check'
    [[ $(git config --global user.name) ]] || echo ERROR: git user.name missing
    [[ $(git config --global user.email) ]] || echo ERROR: git user.email missing
    [[ $(git config --global pull.rebase) == true ]] || echo WARNING: git pull.rebase != true
    [[ $(git config --global rebase.autosquash) == true ]] ||
        echo WARNING: git rebase.autosquash != true
    [[ $(git config --global push.default) == current ]] ||
        echo WARNING: git push.default != current
    [[ -f ~/.config/git/ignore ]] || echo WARNING: global git ignore file absent
    if [[ $OS == Darwin ]]; then
        grep --fixed-strings --no-messages --quiet '.DS_Store' ~/.config/git/ignore ||
            echo WARNING: .DS_Store files not globally git ignored
        [[ $(defaults read NSGlobalDomain ApplePressAndHoldEnabled) == '0' ]] ||
            echo WARNING: MacOS press and hold enabled
        [[ $(defaults read NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled) == '0' ]] ||
            echo WARNING: MacOS period substitution enabled
        [[ $(defaults read NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled) == '0' ]] ||
            echo WARNING: MacOS quote substitution enabled
    fi
}

forceready() {
    : 'FORCE system to be READY for development, clobbering current settings'
    [[ -n $INSH_NAME ]] || git config --global user.name "$INSH_NAME"
    [[ -n $INSH_EMAIL ]] || git config --global user.email "$INSH_EMAIL"
    git config --global pull.rebase true
    git config --global rebase.autosquash true
    git config --global push.default current
    [[ -d ~/.config/git ]] || mkdir -p ~/.config/git

    if [[ $OS == Darwin ]]; then
        [[ -f ~/.config/git/ignore ]] || curl -so ~/.config/git/ignore \
            https://raw.githubusercontent.com/github/gitignore/master/Global/macOS.gitignore
        defaults write NSGlobalDomain ApplePressAndHoldEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled -bool false
        defaults write NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled -bool false
    fi
}

ghas() {
    : 'GitHub Action Summary'
    # TODO use the variables, maybe after calling a helper function that sets them
    cat <<EOD >> "$GITHUB_STEP_SUMMARY"
| Variable      | Value                                          |
| ------------- | ---------------------------------------------- |
| CODEname      | $GITHUB_REPOSITORY |
| Git hASH      | $GITHUB_SHA |
| TAg or BRanch | $GITHUB_REF |
EOD
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

resourcerun() {
    : 'RE-SOURCE this file and RUN the specified function with tracing enabled'
    # shellcheck source=includes.sh
    source "${BASH_SOURCE[0]}"
    set -x
    "$@"
    set +x
}

wg() {
    : 'With Git hash (gash) set'
    old_gash=$gash
    gash=$(git describe --match=- --always --abbrev=40 --dirty)
    export gash
    "$@"
    gash=$old_gash
}
