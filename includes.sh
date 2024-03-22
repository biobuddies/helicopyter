# shellcheck shell=bash

# TODO check for bash
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

cona() {
    : 'CodeNAme'
    if [[ $GITHUB_REPOSITORY ]]; then
        echo "${GITHUB_REPOSITORY##*/}"
    else
        echo "$VIRTUAL_ENV" | sed -E 's,.*/([^/]+)/\.?venv,\1,'
    fi
}

devready() {
    : 'DEVelopment READYness check'
    [[ $0 == bash ]] || echo 'ERROR: not running in BASH
Testing multiple shells is a lot of work, and shellcheck does not support zsh.'
    [[ $(git config --global advice.skipCherryPicks) == true ]] ||
        echo 'WARNING: git advice.skipCherryPicks != true
This reduces noise when pull requests are squashed on the server side.'
    [[ $(git config --global core.commentChar) == ';' ]] ||
        echo 'WARNING: git core.commentChar != ;
This allows # hash character to be used for Markdown headers'
    [[ $(git config --global diff.colormoved) == zebra ]] ||
        echo 'WARNING: git diff.colormoved != zebra
This distinguishes moved lines from added and removed lines'
    [[ $(git config --global user.name) ]] ||
        echo 'ERROR: git user.name missing
Inconsistency breaks reports like git shortlog'
    [[ $(git config --global user.email) ]] ||
        echo 'ERROR: git user.email missing
Inconsistency breaks reports like git shortlog'
    [[ $(git config --global pull.rebase) == true ]] ||
        echo 'WARNING: git pull.rebase != true
Always be rebasing'
    [[ $(git config --global push.default) == current ]] ||
        echo 'WARNING: git push.default != current
Use feature branches with "GitHub Flow"'
    [[ $(git config --global rebase.autosquash) == true ]] ||
        echo 'WARNING: git rebase.autosquash != true
Act on "fixup!" and "squash!" commit title prefixes'
    if [[ $OS == Darwin ]]; then
        grep --fixed-strings --no-messages --quiet .DS_Store ~/.config/git/ignore ||
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
    if [[ $0 != bash ]]; then
        chsh -s /bin/bash
        echo 'Shell changed to BASH. Please restart your shell and rerun forceready.'
        # TODO could we run this function with bash?
        return
    fi

    git config --global advice.skipCherryPicks true
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

ghas() {
    : 'GitHub Action Summary'
    cat <<EOD >> "$GITHUB_STEP_SUMMARY"
| FLAN | Unabbrev.  | Value                                          |
| -----|----------- | ---------------------------------------------- |
| cona | COdeNAme   | $(cona) |
| gash | Git hASH   | $(gash) |
| tabr | TAg/BRanch | $(tabr) |
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

tabr() {
    : 'TAg or BRanch or empty string'
    # GITHUB_HEAD_REF works for Pull Requests, GITHUB_REF_NAME for all the other triggers
    # https://stackoverflow.com/questions/58033366
    echo "${GITHUB_HEAD_REF:-$GITHUB_REF_NAME}"
    # TODO how should people set this locally?
}
