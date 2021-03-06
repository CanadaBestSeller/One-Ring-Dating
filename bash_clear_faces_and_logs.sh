#!/usr/bin/env bash

rm *.log > /dev/null 2>&1
rm *.blacklist > /dev/null 2>&1
rm -r phase_1_faces > /dev/null 2>&1\


if [[ "$1" == "all" ]]; then
	echo "'clean all specified. Removing libraries."
    rm -r code/one_ring_virtual_env > /dev/null 2>&1;
    rm -r code/one_ring_modules.egg-info > /dev/null 2>&1;
    rm -r code/one_ring_modules/__pycache__ > /dev/null 2>&1;
else
    echo "'all' is not supplied. NOT removing libraries"
fi

echo "clean finished."