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

alias ls='ls --color=auto'
alias pca='pre-commit run --all-files'
alias pcm='pre-commit run --all-files --hook-stage manual'

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

    [[ $(command -v deactivate) ]] && deactivate

    if [[ -f $directory/.venv/bin/activate ]]; then
        # shellcheck disable=SC1091
        source "$directory/.venv/bin/activate"
        python --version
    fi
}

devready() {
    : DEVelopment READYness check
    [[ $(git config --global user.name) ]] || echo ERROR: git user.name missing
    [[ $(git config --global user.email) ]] || echo ERROR: git user.email missing
    [[ $(git config --global pull.rebase) == true ]] || echo WARNING: git pull.rebase != true
    [[ $(git config --global rebase.autosquash) == true ]] || echo WARNING: git rebase.autosquash != true
    [[ $(git config --global push.default) == upstream ]] || echo WARNING: git push.default != upstream
}

resourcerun() {
    : RE-SOURCE this file and RUN the specified function with tracing enabled
    # shellcheck source=includes.sh
    source "${BASH_SOURCE[0]}"
    set -x
    "$@"
    set +x
}
