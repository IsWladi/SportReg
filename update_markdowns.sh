#!/bin/bash

# Define the base URL and the output directory
BASE_URL="http://localhost/api/markdown/get/workouts"
OUTPUT_DIR="/home/iswladi/Documents/Entrenamientos"

# Create the output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Array of current users
CURRENT_USERS=("wladi" "mime" "mama")

# Loop through each current user and make a request
for USER in "${CURRENT_USERS[@]}"
do
  # Define the output file path
  OUTPUT_FILE="$OUTPUT_DIR/$USER.md"

  # Make the curl request and save the response
  curl -X 'GET' \
    "$BASE_URL?current_user=$USER&lang=es" \
    -H 'accept: text/markdown' \
    -o "$OUTPUT_FILE"
done
