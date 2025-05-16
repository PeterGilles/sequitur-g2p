#!/usr/bin/env python
"""
Clean up input text files for g2p_sentences.py by:
1. Converting to lowercase
2. Removing punctuation
"""

import sys
import re
import string

def clean_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Define punctuation (including special quotes)
    punctuation = string.punctuation + "„""‚''«»"
    
    # Replace punctuation with spaces
    for p in punctuation:
        text = text.replace(p, " ")
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f_in:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                cleaned = clean_text(line.strip())
                if cleaned:
                    f_out.write(cleaned + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleanup_input.py input_file output_file")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    process_file(input_file, output_file)
    print(f"Processed {input_file} -> {output_file}")