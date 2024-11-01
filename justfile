# Configuration
# set shell := ["bash", "-uc"]

# Environment Variables
export PACKAGES := "bind9-host curl fping git less tmux tree"

# Get operating system
OS := `uname -s`

# Default recipe (shows available recipes)
default:
    @just --list

# Development Environment Setup
[private]
_ensure-homebrew:
    #!/usr/bin/env bash
    if [[ "{{OS}}" == "Darwin" && ! -x $(command -v brew) ]]; then
        [[ -d /opt/homebrew/bin ]] && export PATH="/opt/homebrew/bin:$PATH"
        [[ -x $(command -v brew) ]] || echo "ERROR: homebrew missing"
    fi

# Activate virtual environment after changing directory
a:
    #!/usr/bin/env bash
    echo $SHELL $BASH_VERSION
    check_conda=$(command -v conda)
    echo $check_conda
    [[ $(command -v conda) ]] && conda deactivate
    might_be_file=$(command -v deactivate)
    if [[ "${might_be_file}" ]]; then
        if [[ -f "${might_be_file}" ]]; then
            source deactivate
        else
            deactivate
        fi
    fi
    if [[ -f .venv/bin/activate ]]; then
        source .venv/bin/activate
        just pathver python .python-version
    elif [[ -d conda ]]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
        conda activate "$(basename "$PWD")"
        just pathver python .python-version
    fi
    if [[ -f .nvmrc ]]; then
        just pathver node .nvmrc
    fi

# print PATH and VERsion; optionally assert version file matches
pathver command version_file="":
    #!/usr/bin/env bash
    source=$(type -p "{{command}}")
    if [[ -z $source ]]; then
        source=$(type "{{command}}")
    fi
    actual_version=$("{{command}}" --version 2>&1 | gsed -En 's/(.+ )?(v?[0-9]+\.[0-9]+\.[^ ]+).*/\2/p')
    echo "$source $actual_version"
    if [[ -f "{{version_file}}" ]]; then
        expected_version=$(cat "{{version_file}}")
        if [[ $actual_version != "$expected_version" ]]; then
            echo "ERROR: $source version $actual_version does not match {{version_file}} $expected_version"
            exit 1
        fi
    fi

# Docker Compose Build
dcb *args:
    docker compose --progress=plain build {{args}}

# Docker Compose Push
dcp *ARGS:
    docker compose push --quiet {{ARGS}}

# Docker Compose Run, respecting docker-compose.yaml port definitions
dcr *ARGS:
    docker compose run --quiet-pull --service-ports {{ARGS}}

# Docker Compose Shell
dcs *ARGS:
    docker compose run "$(just cona)" bash {{ARGS}}

# Docker Compose Up
dcu *ARGS:
    docker compose up {{ARGS}}

# DEVelopment READYness check
devready:
    #!/usr/bin/env bash
    set -euo pipefail
    
    grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
        || echo 'WARNING: legacy_version_file != yes'
    
    installed=$(asdf plugin list 2>/dev/null)
    [[ $installed == *nodejs* ]] || echo 'WARNING: nodejs plugin for asdf not added'
    [[ $installed == *tenv* ]] || echo 'WARNING: tenv plugin for asdf not added'
    [[ $installed == *uv* ]] || echo 'WARNING: uv plugin for asdf not added'
    
    # Git configs
    [[ $(git config --global advice.skippedCherryPicks) == false ]] \
        || echo 'WARNING: git advice.skippedCherryPicks != false'
    [[ $(git config --global core.commentChar) == ';' ]] \
        || echo 'WARNING: git core.commentChar != ;'
    [[ $(git config --global diff.colormoved) == zebra ]] \
        || echo 'WARNING: git diff.colormoved != zebra'
    [[ $(git config --global user.name) ]] \
        || echo 'ERROR: git user.name missing'
    [[ $(git config --global user.email) ]] \
        || echo 'ERROR: git user.email missing'
    [[ $(git config --global pull.rebase) == true ]] \
        || echo 'WARNING: git pull.rebase != true'
    [[ $(git config --global push.default) == current ]] \
        || echo 'WARNING: git push.default != current'
    [[ $(git config --global rebase.autosquash) == true ]] \
        || echo 'WARNING: git rebase.autosquash != true'

# FORCE system to be READY for development, clobbering current settings
forceready:
    #!/usr/bin/env bash
    set -euo pipefail
    
    grep -qE 'legacy_version_file.*=.*yes' ~/.asdfrc 2>/dev/null \
        || echo 'legacy_version_file = yes' >>~/.asdfrc
    
    installed=$(asdf plugin list 2>/dev/null)
    [[ $installed == *nodejs* ]] || asdf plugin add nodejs
    [[ $installed == *tenv* ]] || asdf plugin add tenv https://github.com/tofuutils/asdf-tenv
    [[ $installed == *uv* ]] || asdf plugin add uv
    
    git config --global advice.skippedCherryPicks false
    git config --global core.commentChar ';'
    git config --global diff.colormoved zebra
    [[ -z "${INSH_NAME:-}" ]] || git config --global user.name "$INSH_NAME"
    [[ -z "${INSH_EMAIL:-}" ]] || git config --global user.email "$INSH_EMAIL"
    git config --global pull.rebase true
    git config --global push.default current
    git config --global rebase.autosquash true
    
    mkdir -p ~/.config/git

# print CodeNAme, a four letter acronym
cona:
    #!/usr/bin/env bash
    if [[ $GITHUB_REPOSITORY ]]; then
        echo "${GITHUB_REPOSITORY##*/}"
    elif [[ $VIRTUAL_ENV ]]; then
        basename "${VIRTUAL_ENV%/.venv}"
    else
        basename "$PWD"
    fi

# print ENVIronment, a four letter acronym
envi:
    #!/usr/bin/env bash
    if [[ $ENVI ]]; then
        echo "$ENVI"
    elif [[ $GITHUB_ACTIONS ]]; then
        echo github
    else
        echo local
    fi

# print Git hASH, a four letter acronym
gash:
    git describe --abbrev=40 --always --dirty --match=-

# %G %V COUNT style version string; see also: yucount
gvcount:
    #!/usr/bin/env bash
    gv=$(date -u +v%G.%V.)
    git fetch --tags
    count=$(git tag --list "$gv*" | sed "s/$gv//" | sort -r | head -1)
    echo "$gv$((${count:-0} + 1))"

# %Y %U COUNT style version string; see also: gvcount
yucount:
    #!/usr/bin/env bash
    yu=$(date -u +v%Y.%U.)
    git fetch --tags
    count=$(git tag --list "$yu*" | sed "s/$yu//" | sort -r | head -1)
    echo "$yu$((${count:-0} + 1))"

# run Pre-Commit on modified files
pc *ARGS:
    pre-commit run {{ARGS}}

# run Pre-Commit on All files
pca *args:
    pre-commit run --all-files {{args}}

# run Pre-Commit on All files including Manual stage hooks
pcam *ARGS:
    pre-commit run --all-files --hook-stage manual {{ARGS}}

# run Pre-Commit on modified files including Manual stage hooks
pcm *ARGS:
    pre-commit run --hook-stage manual {{ARGS}}

# Uv Pip Compile
upc:
    #!/usr/bin/env bash
    uv pip compile -o requirements.txt --python-platform linux requirements.in
    if [[ "{{OS}}" == "Darwin" ]]; then
        appnope=$(uv pip freeze | grep appnope)
        [[ $appnope ]] && echo "$appnope" >requirements-macos.txt
    fi

# Uv Pip Sync, with MacOS workaround for appnope
ups *ARGS:
    #!/usr/bin/env bash
    if [[ "{{OS}}" == "Darwin" && -f requirements-macos.txt ]]; then
        uv pip sync {{ARGS}} requirements.txt requirements-macos.txt
    else
        uv pip sync {{ARGS}} requirements.txt
    fi

# Helicopyter synth and Terraform Apply
hta cona envi *ARGS:
    #!/usr/bin/env bash
    if [[ "{{envi}}" == "default" ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        exit 1
    fi
    python -m helicopyter --format_with="${INSH_TF:-terraform}" "{{cona}}" \
        && TF_WORKSPACE="{{envi}}" ${INSH_TF:-terraform} -chdir="deploys/{{cona}}/terraform" apply {{ARGS}}

# Helper for Terraform Init
hti cona *ARGS:
    ${INSH_TF:-terraform} -chdir="deploys/{{cona}}/terraform" init {{ARGS}}

# Helicopyter synth and Terraform Plan
htp cona envi *ARGS:
    #!/usr/bin/env bash
    if [[ "{{envi}}" == "default" ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        exit 1
    fi
    python -m helicopyter --format_with="${INSH_TF:-terraform}" "{{cona}}" \
        && TF_WORKSPACE="{{envi}}" ${INSH_TF:-terraform} -chdir="deploys/{{cona}}/terraform" plan {{ARGS}}

# Universally Unique IDentifier
uuid:
    python -c 'import uuid; print(uuid.uuid4())'

# SUMMARIZE environment by displaying four letter acronyms
summarize:
    #!/usr/bin/env bash
    CONA=$(just cona)
    ENVI=$(just envi)
    GASH=$(just gash)
    TABR=$(just tabr)
    cat <<EOD | tee "${GITHUB_STEP_SUMMARY:-/dev/null}"
    | FLAN | Unabbrevia. | Value                                          |
    | ---- | ----------- | ---------------------------------------------- |
    | CONA | COdeNAme    | $CONA |
    | ENVI | ENVIronment | $ENVI |
    | GASH | Git hASH    | $GASH |
    | ROLE | ROLE        | $ROLE |
    | TABR | TAg/BRanch  | $TABR |
    EOD
    if [[ $GITHUB_ENV ]]; then
        echo -e "CONA=$CONA\nGASH=$GASH\nTABR=$TABR" >>"$GITHUB_ENV"
    fi

# Alias for summarize (backwards compatibility)
ghas: summarize

# print TAg or BRanch or empty string, a four letter acronym
tabr:
    #!/usr/bin/env bash
    if [[ $GITHUB_HEAD_REF ]]; then
        echo "$GITHUB_HEAD_REF"
    elif [[ $GITHUB_REF_NAME ]]; then
        echo "$GITHUB_REF_NAME"
    else
        description=$(git describe --all --dirty --exact-match 2>/dev/null)
        [[ $description == *-dirty ]] || echo "${description#*/}"
    fi
