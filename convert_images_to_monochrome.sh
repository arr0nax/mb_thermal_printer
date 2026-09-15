#!/bin/bash

# Folder containing cmc folders which contain card art
ART_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/art"

# Target specific subfolder if provided as an argument (e.g., ./convert_images_to_monochrome.sh 3)
if [ -n "$1" ]; then
    target_dirs=("${ART_ROOT}/$1")
else
    target_dirs=("${ART_ROOT}"/*)
fi

# Collect only images that still need conversion so skipped files stay silent.
pending_files=()
for dir in "${target_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "Checking for unconverted cards in: $dir"
        for jpg_file in "${dir}"/*.jpg; do
            if [ -f "$jpg_file" ]; then
                output_file="${dir}/converted_files/$(basename -- "$jpg_file" .jpg).bmp"
                if [ ! -f "$output_file" ]; then
                    pending_files+=("$jpg_file")
                fi
            fi
        done
    fi
done

total=${#pending_files[@]}
completed=0
bar_width=20
for jpg_file in "${pending_files[@]}"; do
    dir=$(dirname "$jpg_file")
    output_file="${dir}/converted_files/$(basename -- "$jpg_file" .jpg).bmp"
    mkdir -p "${dir}/converted_files"

    completed=$((completed + 1))
    filled=$((completed * bar_width / total))
    empty=$((bar_width - filled))
    filled_bar=$(printf '%*s' "$filled" '' | tr ' ' '#')
    empty_bar=$(printf '%*s' "$empty" '')
    printf '\rConverting [%s%s] %d/%d %s' "$filled_bar" "$empty_bar" "$completed" "$total" "$(basename "$jpg_file")"

    # +level lifts the black floor and brightens the image.
    convert "$jpg_file" -resize 384x -colorspace Gray +level 20%,100% -gamma 2.0 -ordered-dither o8x8 "$output_file"

    if [ $? -ne 0 ]; then
        printf '\nError converting: %s\n' "$jpg_file"
    fi
done

if [ "$total" -gt 0 ]; then
    printf '\n'
fi

