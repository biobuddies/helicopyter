# shellcheck shell=bash

case $(uname -s) in
    Darwin)
        export BASH_SILENCE_DEPRECATION_WARNING=1

    if ! [[ -x $(command -v brew) ]]; then
        [[ -d /opt/homebrew/bin ]] && export PATH="/opt/homebrew/bin:$PATH"
        [[ -x $(command -v brew) ]] || echo ERROR: homebrew missing
    fi
esac

if ! [[ -x $(command -v nvm) ]]; then
    NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
    # shellcheck disable=SC1091
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" || echo ERROR: nvm missing
fi

# F: no-op for single page, R: color, X: keep text when exiting, i: case insensitive searching
LESS="-FRXi"
export LESS

# Aliases only work in interactive shells
alias jq='jq --color-output'
alias ls='ls --color=auto'

pathver() {
    : Print path and version
    (type "$1" && "$1" --version) |
        sed -Ee N -e 's,^[^/(]*,,' -e 's,\((.+)\),\1,' -e 's/\n/ /'
}

a() {
    : Activate virtual environment after changing directory

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

    # TODO pyenv-virtualenv wants `. deactivate`
    # TODO conda wants `conda deactivate`
    [[ $(command -v deactivate) ]] && deactivate

    if [[ -f .venv/bin/activate ]]; then
        # shellcheck disable=SC1091
        source .venv/bin/activate
        pathver python
    elif [[ -d conda ]]; then
        # shellcheck disable=SC1091
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate "$(basename "$directory")"
        pathver python
    fi

    if [[ -f .nvmrc ]]; then
        nvm install &>/dev/null && nvm use &>/dev/null
        pathver node
    fi
}

devready() {
    : DEVelopment READYness check
    [[ $(git config --global user.name) ]] || echo ERROR: git user.name missing
    [[ $(git config --global user.email) ]] || echo ERROR: git user.email missing
    [[ $(git config --global pull.rebase) == true ]] || echo WARNING: git pull.rebase != true
    [[ $(git config --global rebase.autosquash) == true ]] || echo WARNING: git rebase.autosquash != true
    [[ $(git config --global push.default) == current ]] || echo WARNING: git push.default != current
}

pc() {
    : run Pre-Commit on modified files
    pre-commit run "$@"
}

pca() {
    : run Pre-Commit on All files
    pre-commit run --all-files "$@"
}

pcam() {
    : run Pre-Commit on All files including Manual stage hooks
    pre-commit run --all-files --hook-stage manual "$@"
}

pcm() {
    : run Pre-Commit on modified files including Manual stage hooks
    pre-commit run --hook-stage manual "$@"
}

resourcerun() {
    : RE-SOURCE this file and RUN the specified function with tracing enabled
    # shellcheck source=includes.sh
    source "${BASH_SOURCE[0]}"
    set -x
    "$@"
    set +x
}
