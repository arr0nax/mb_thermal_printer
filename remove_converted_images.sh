#!/bin/bash

# Folder containing cmc folders which contain card art
ART_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/art"

# Target specific subfolder if provided as an argument (e.g., ./remove_converted_images.sh 3)
if [ -n "$1" ]; then
    target_dirs=("${ART_ROOT}/$1")
else
    target_dirs=("${ART_ROOT}"/*)
fi

# Iterate through subdirectories and remove converted BMPs
for dir in "${target_dirs[@]}"; do
    converted_dir="${dir}/converted_files"
    if [ -d "$converted_dir" ]; then
        bmp_count=$(find "$converted_dir" -maxdepth 1 -name "*.bmp" | wc -l | tr -d ' ')
        if [ "$bmp_count" -gt 0 ]; then
            echo "Removing $bmp_count BMP(s) from: $converted_dir"
            rm -f "${converted_dir}"/*.bmp
        else
            echo "No BMP files found in: $converted_dir"
        fi
    else
        echo "No converted_files directory in: $dir"
    fi
done
