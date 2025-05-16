# Sequitur G2P for Luxembourgish

This repository provides a Grapheme-to-Phoneme (G2P) conversion system for the Luxembourgish language, built upon the Sequitur G2P framework developed at RWTH Aachen University.

## Overview

The Luxembourgish G2P converter allows you to:
- Convert Luxembourgish text to phonetic transcriptions
- Process both individual words and complete sentences
- Handle special Luxembourgish characters (ë, é, ä, etc.)
- Clean and preprocess text for optimal conversion
- Process large files with comprehensive error handling

## Components

This package consists of three main components:

1. **Pre-trained Luxembourgish model** (`model-8`): A model trained on thousands of Luxembourgish words and their phonetic transcriptions

2. **Sentence-level processor** (`g2p_sentences.py`): An extension of the Sequitur G2P system that allows processing entire sentences, maintaining the original sentence structure in the output

3. **Text cleaning utility** (`cleanup_input.py`): A preprocessing tool that converts text to lowercase, removes punctuation (including special Luxembourgish quotes), and normalizes whitespace

## Installation

1. Clone this repository:
```bash
git clone https://github.com/PeterGilles/sequitur-g2p.git
cd sequitur-g2p
```

2. Install the package and dependencies:
```bash
pip install -e .
```

## Usage

### Converting Individual Words

```bash
python g2p.py --model model-8 --word "Lëtzebuerg"
```
Output:
```
Lëtzebuerg	l ə ts ə b uː ɐ̯ ɕ
```

### Converting Word Lists

Create a file with one word per line, then run:
```bash
python g2p.py --model model-8 --apply words.txt > phonemes.txt
```

### Converting Sentences

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

## Example

### Input (Luxembourgish text):
```
Gudde Moien! Ech si frou, fir hei ze sinn.
Lëtzebuerg ass e schéint Land mat vill Kultur.
```

### After text cleaning:
```
gudde moien ech si frou fir hei ze sinn
lëtzebuerg ass e schéint land mat vill kultur
```

### Output (Phonetic transcription):
```
gudde moien ech si frou fir hei ze sinn	ɡ u d ə # m ɔɪ ə n # ə ɕ # z iː # f ʀ əʊ # f iː ɐ̯ # h aɪ # ts ə # z i n
lëtzebuerg ass e schéint land mat vill kultur	l ə ts ə b uː ɐ̯ ɕ # ɑ s # ə # ʃ ɜɪ n t # l ɑ n t # m ɑ t # f i l # k u l t uː ɐ̯
```

## Error Handling and Verification

The tool provides comprehensive error handling and verification:

- Detailed error reporting for file operations and word processing
- Line counting in input and output files
- Verification that input and output line counts match
- Statistics on words processed, successful conversions, and errors

Example output:
```
INFO: Input file contains 100 non-empty lines
INFO: Processed 100 lines total (2 empty lines skipped) with 824 words

Processing Summary:
  Input lines: 100
  Output lines: 100
  Total words processed: 824
  Successfully converted words: 824
  Failed conversions: 0
  Total errors: 0
SUCCESS: Input and output line counts match (100 lines).
```

## Documentation

For more detailed information about the original Sequitur G2P system, please refer to:

```
M. Bisani and H. Ney: "Joint-Sequence Models for Grapheme-to-Phoneme Conversion".
Speech Communication, Volume 50, Issue 5, May 2008, Pages 434-451
```

## License

This software is distributed under the GNU General Public License Version 2 (June 1991) as published by the Free Software Foundation. See the LICENSE file for details.