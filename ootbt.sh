#!/bin/sh
set +e
# Out of the box test script.

TARBALL="$1"
if [ -z "${TARBALL}" ]; then
    echo "Usage: ootbt.sh TARBALL"
    exit 1
fi

if ! which python3 >/dev/null 2>&1 ; then
    echo "ootbt.sh: missing script requirement: python3"
    exit 1
fi
if ! which virtualenv >/dev/null 2>&1 ; then
    echo "ootbt.sh: missing script requirement: virtualenv"
    exit 1
fi

TARBALL="$(readlink -m "${TARBALL}")"
WORKDIR="$(mktemp -d)"
trap "{ rm -r ${WORKDIR}; }" EXIT
cd "${WORKDIR}"

VENV="${WORKDIR}/.venv"
virtualenv -p python3 "${VENV}"
. "${VENV}"/bin/activate

tar xf "${TARBALL}"
cd porting-advisor-*

if ! python3 setup.py install; then
    echo "FAIL: setup.py install exited with failure exit code $?."
    exit 1
fi

if ! which porting-advisor >/dev/null 2>&1; then
    echo "FAIL: install did not add porting-advisor to PATH."
    exit 1
fi

SRCDIR="${WORKDIR}/src"
mkdir "${SRCDIR}"

OUTPUT="$(porting-advisor "${SRCDIR}" 2>&1)"
if ! echo "${OUTPUT}" | grep "0 files scanned." >/dev/null; then
    echo 'FAIL: expected "0 files scanned." output when scanning empty source directory.'
    exit 1
fi
if ! echo "${OUTPUT}" | grep "No issues found." >/dev/null; then
    echo 'FAIL: expected "No issues found." output when scanning empty source directory.'
    exit 1
fi

cat >"${SRCDIR}/otherarch.s" <<__ASM__
mov %ra,%rb
__ASM__

OUTPUT="$(porting-advisor "${SRCDIR}" 2>&1)"
if ! echo "${OUTPUT}" | grep "1 files scanned." >/dev/null; then
    echo 'FAIL: expected "1 files scanned." output when scanning assembly source file.'
    exit 1
fi
if ! echo "${OUTPUT}" | grep "architecture-specific assembly source file" >/dev/null; then
    echo 'FAIL: expected "architecture-specific assembly source file" output when scanning assembly source file.'
    exit 1
fi

REPORT_HTML="${WORKDIR}/report.html"

OUTPUT="$(porting-advisor --output "${REPORT_HTML}" "${SRCDIR}")"
if [ ! -z "${OUTPUT}" ]; then
    echo "FAIL: expected no output on stdout when generating HTML report."
    exit 1
fi
if [ ! -f "${REPORT_HTML}" ]; then
    echo "FAIL: expected --output report.html to generate HMTL report."
    exit 1
fi
if ! grep "1 files scanned." "${REPORT_HTML}" >/dev/null; then
    echo 'FAIL: expected "1 files scanned." in HTML report when scanning assembly source file.'
    exit 1
fi
if ! grep "architecture-specific assembly source file" "${REPORT_HTML}" >/dev/null; then
    echo 'FAIL: expected "architecture-specific assembly source file" in HTML report when scanning assembly source file.'
    exit 1
fi

echo "PASS"
exit 0
