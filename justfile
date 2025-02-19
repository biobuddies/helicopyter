set export
set shell := ['bash', '-euo', 'pipefail', '-c']

OS := `uname -s`
PACKAGES := "bind9-host curl fping git less tmux tree"

default:
    @just --list

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
    # TODO investigate require() instead
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
dcp *args:
    docker compose push --quiet {{args}}

# Docker Compose Run, respecting docker-compose.yaml port definitions
dcr *args:
    docker compose run --quiet-pull --service-ports {{args}}

# Docker Compose Shell
dcs *args:
    docker compose run "$(just cona)" bash {{args}}

# Docker Compose Up
dcu *args:
    docker compose up {{args}}

# DEVelopment READYness check
devready:
    bash includes.sh devready

# FORCE system to be READY for development, clobbering current settings
forceready:
    bash includes.sh forceready

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

# print GIt HAsh, a four letter acronym
giha:
    git describe --abbrev=40 --always --dirty --match=-

gash: giha  # Backwards compatibility

# run Pre-Commit on modified files
pc *args:
    pre-commit run {{args}}

# run Pre-Commit on All files
pca *args:
    pre-commit run --all-files {{args}}

# run Pre-Commit on All files including Manual stage hooks
pcam *args:
    pre-commit run --all-files --hook-stage manual {{args}}

# run Pre-Commit on modified files including Manual stage hooks
pcm *args:
    pre-commit run --hook-stage manual {{args}}

# Uv Pip Compile
upc *args:
    uv pip compile --all-extras --output-file requirements.txt --python-platform linux \
        pyproject.toml {{ \
            if path_exists('requirements.in') == 'true' { 'requirements.in' } else { '' } \
        }} {{args}}

# Uv Pip Sync
ups *args:
    uv pip sync {{args}} requirements.txt

# Helicopyter Synth
hs cona='all':
    python -m helicopyter --format_with=${INSH_TF:-terraform} {{cona}}

# Helicopyter synth and Terraform Apply
hta cona envi *args:
    #!/usr/bin/env bash
    if [[ "{{envi}}" == "default" ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        exit 1
    fi
    just hs {{cona}} \
        && TF_VAR_giha=$(just giha) TF_VAR_tabr=$(just tabr) TF_WORKSPACE={{envi}} \
            ${INSH_TF:-terraform} -chdir=deploys/{{cona}}/terraform apply {{args}}

# Helper for Terraform Init and synth
hti cona *args:
    ${INSH_TF:-terraform} -chdir=deploys/{{cona}}/terraform init {{args}}
    just hs {{cona}}

# Helicopyter synth and Terraform Plan
htp cona envi *args:
    #!/usr/bin/env bash
    if [[ "{{envi}}" == "default" ]]; then
        echo 'The default workspace behaves inconsistently.'
        echo 'If you only have one environment, please name it `prod`.'
        exit 1
    fi
    just hs {{cona}} \
        && TF_WORKSPACE={{envi}} ${INSH_TF:-terraform} -chdir=deploys/{{cona}}/terraform plan {{args}}

# Universally Unique IDentifier
uuid:
    @echo {{uuid()}}

# SUMMARIZE environment by displaying four letter acronyms
summarize:
    bash includes.sh summarize

# Alias for summarize (backwards compatibility)
ghas: summarize

# TODO test if these special cases can be dropped
github_reference := env('GITHUB_HEAD_REF', env('GITHUB_REF_NAME', ''))
# print TAg or BRanch or empty string, a four letter acronym
tabr:
    @# remotes/origin/mybranch -> mybranch
    @# heads/mybranch -> mybranch
    @# tags/v2025.02.03 -> v2025.02.03
    @# heads/mybranch-dirty -> '' #empty string
    @echo {{ if github_reference == '' { \
        `git describe --all --dirty --exact-match 2>/dev/null \
            | sed -En '/-dirty$/ q; s,(remotes/[^/]+|heads|tags)/,,p'` \
    } else { github_reference } }}

test:
    python -m pytest --cov=helicopyter --cov-report=term-missing:skip-covered --verbose
