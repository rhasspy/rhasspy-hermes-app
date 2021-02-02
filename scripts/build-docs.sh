#!/usr/bin/env bash
set -e

# Directory of *this* script
this_dir="$( cd "$( dirname "$0" )" && pwd )"
src_dir="$(realpath "${this_dir}/..")"

venv="${src_dir}/.venv"
if [[ -d "${venv}" ]]; then
    echo "Using virtual environment at ${venv}"
    source "${venv}/bin/activate"
fi

# -----------------------------------------------------------------------------

docs_dir="${src_dir}/docs"
build_dir="${docs_dir}/build"
rstcheck -r "${src_dir}/README.rst" "${docs_dir}"
sphinx-build -b linkcheck "${docs_dir}" "${build_dir}/linkcheck"
sphinx-build -n "${docs_dir}" "${build_dir}"

# -----------------------------------------------------------------------------

echo "OK"
