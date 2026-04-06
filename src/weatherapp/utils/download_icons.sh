#!/usr/bin/env bash
# Download Open-Meteo weather icon SVGs locally for PyQt6 GUI (current + forecast)

set -e

ICON_DIR="$HOME/Projects/WeatherApp/src/weatherapp/icons"
mkdir -p "$ICON_DIR"

# GitHub raw folder URL of the entire svg directory
BASE="https://api.github.com/repos/erikflowers/weather-icons/contents/svg"

echo "Fetching list of SVG files..."

# Grab metadata, filter SVGs, download them
curl -s "$BASE" | \
    grep '"download_url"' | \
    cut -d '"' -f 4 | \
    while read -r url; do
        filename=$(basename "$url")
        echo "Downloading $filename ..."
        wget -q -O "$ICON_DIR/$filename" "$url"
    done

echo "Done! All SVGs saved to $ICON_DIR"
