#!/bin/bash
# Gets all flags

SCRIPT_DIR=$(dirname $0)
cd ${SCRIPT_DIR}

# Colors
RESET=$(tput sgr0)
RED="\e[91m"
GREEN="\e[92m"

for solver in $(ls -1 bandit{0..23}/solution.py | sort -V);
do
    output=$(./${solver} 2>/dev/null)
    level=$(dirname $solver)

    IFS=$'\n'
    for s in ${output};
    do
	if [[ "${s}" =~ "Flag =" ]]; then
	    printf "%s : ${GREEN}%s${RESET}\n" "${level}" "${s#*=}"
	fi
    done
done
