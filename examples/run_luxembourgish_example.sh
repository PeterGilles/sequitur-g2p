#!/bin/bash
# Example script to demonstrate the Luxembourgish G2P pipeline

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Input and output files
INPUT_FILE="$SCRIPT_DIR/luxembourgish_example.txt"
CLEANED_FILE="$SCRIPT_DIR/luxembourgish_example_cleaned.txt"
OUTPUT_FILE="$SCRIPT_DIR/luxembourgish_example_phonemes.txt"

# Model path
MODEL_FILE="$PARENT_DIR/model-8"

echo "Luxembourgish G2P Example Pipeline"
echo "=================================="
echo

# Step 1: Clean the input text
echo "Step 1: Cleaning input text..."
python "$PARENT_DIR/cleanup_input.py" "$INPUT_FILE" "$CLEANED_FILE"

# View the cleaned text
echo
echo "Original text:"
cat "$INPUT_FILE"
echo
echo "Cleaned text:"
cat "$CLEANED_FILE"
echo

# Step 2: Run G2P conversion
echo "Step 2: Running G2P conversion..."
python "$PARENT_DIR/g2p_sentences.py" --model "$MODEL_FILE" --apply "$CLEANED_FILE" > "$OUTPUT_FILE"

# View the output
echo
echo "G2P Output (Phonetic Transcription):"
cat "$OUTPUT_FILE"
echo
echo "Example completed. Output saved to: $OUTPUT_FILE"