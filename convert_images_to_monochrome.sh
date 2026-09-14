#!/bin/bash

# Folder containing cmc folders which contain card art
ART_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/art"

# Target specific subfolder if provided as an argument (e.g., ./convert_images_to_monochrome.sh 3)
if [ -n "$1" ]; then
    target_dirs=("${ART_ROOT}/$1")
else
    target_dirs=("${ART_ROOT}"/*)
fi

# Iterate through subdirectories
for dir in "${target_dirs[@]}"; do
    # Check if directory is empty
    if [ -d "$dir" ] && [ "$(ls -A "$dir")" ]; then
        # Create a new folder for the converted files
        mkdir -p "${dir}/converted_files"
        
        # Iterate through each JPG file and convert it to a rescaled monochrome bitmap
        for jpg_file in "${dir}"/*.jpg; do
            if [ -f "$jpg_file" ]; then
                echo "Resizing and converting to grayscale for: $jpg_file"
                
                # Define the output filename by replacing the extension with bmp
                output_file="${dir}/converted_files/$(basename -- "$jpg_file" .jpg).bmp"

                if [ -f "$output_file" ]; then
                    echo "Skipping, already converted: $jpg_file"
                    continue
                fi

                # Use ImageMagick's convert command to perform the conversion
                # +level lifts the black floor (e.g., 20% gray minimum) so dark areas don't print solid black
                convert "$jpg_file" -resize 192x -colorspace Gray +level 20%,100% -gamma 2.0 -ordered-dither o8x8 "$output_file"
                
                # Check if conversion was successful
                if [ $? -eq 0 ]; then
                    echo "Conversion successful: $jpg_file"
                else
                    echo "Error converting: $jpg_file"
                fi
            fi
        done
    else
        echo "No JPG files found in directory: $dir"
    fi
done

