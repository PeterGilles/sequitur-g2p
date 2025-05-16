# Sequitur G2P for Luxembourgish

This repository contains an extended version of the Sequitur G2P (Grapheme-to-Phoneme) converter with additional functionality for processing Luxembourgish text.

## New Features

### 1. Sentence-Level Processing

The original Sequitur G2P tool processes words individually. We've added `g2p_sentences.py` which can process entire sentences, converting all words in the input and outputting the results in sentence format. This is particularly useful for preparing data for speech recognition or synthesis systems.

### 2. Error Handling and Verification

The new version includes comprehensive error handling and verification:
- Detailed error reporting for file operations and word processing
- Line counting in input and output files
- Verification that input and output line counts match
- Statistics on words processed, successful conversions, and errors

### 3. Text Cleaning Utility

A separate text cleaning utility (`cleanup_input.py`) is provided to:
- Convert text to lowercase
- Remove punctuation (including Luxembourgish special quotes)
- Normalize whitespace

## Luxembourgish G2P Model

This repository includes a pre-trained G2P model for Luxembourgish (`model-8`). This model was trained on a corpus of Luxembourgish words and their phonetic transcriptions.

## Usage Examples

### Basic Word-by-Word G2P Conversion

```bash
python g2p.py --model model-8 --apply words.txt > phonemes.txt
```

### Processing Sentences

```bash
python g2p_sentences.py --model model-8 --apply sentences.txt > phonemes.txt
```

### Complete Pipeline with Text Cleaning

```bash
# Step 1: Clean the input text
python cleanup_input.py raw_text.txt cleaned_text.txt

# Step 2: Run G2P conversion on the cleaned text
python g2p_sentences.py --model model-8 --apply cleaned_text.txt > phonemes.txt
```

### Converting Single Words

```bash
python g2p_sentences.py --model model-8 --word "Lëtzebuerg"
```

## Example Input and Output

### Input (Luxembourgish text):
```
Wéi geet et dir?
Lëtzebuerg ass e schéint Land.
```

### Output (After G2P conversion):
```
wéi geet et dir	v ɜɪ # ˈ ɡ eː t # ə t # d iː ɐ̯
lëtzebuerg ass e schéint land	ˈ l ə . ts ə . b uː ɐ̯ ɕ # ɑ s # ə # ˈ ʃ ɜɪ n t # l ɑ n t
```

## Error Handling

The updated script provides detailed error messages and statistics:

```
INFO: Input file contains 100 non-empty lines
ERROR: Failed to convert "zxyw": no applicable rules
INFO: Processed 100 lines total (2 empty lines skipped) with 824 words

Processing Summary:
  Input lines: 100
  Output lines: 100
  Total words processed: 824
  Successfully converted words: 823
  Failed conversions: 1
  Total errors: 1
SUCCESS: Input and output line counts match (100 lines).
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/PeterGilles/sequitur-g2p.git
```

2. Install dependencies:
```bash
pip install -e .
```

## License

This software is distributed under the same license as the original Sequitur G2P tool. See the LICENSE file for details.
