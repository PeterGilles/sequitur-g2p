#!/usr/bin/env python

from __future__ import print_function
"""
Grapheme-to-Phoneme Conversion for Sentences

Modified from original g2p.py by Maximilian Bisani to handle full sentences.
"""

__author__ = "Maximilian Bisani"
__version__ = "$LastChangedRevision: 1667 $"
__date__ = "$LastChangedDate: 2007-06-02 16:32:35 +0200 (Sat, 02 Jun 2007) $"
__copyright__ = "Copyright (c) 2004-2005  RWTH Aachen University"
__license__ = """
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License Version 2 (June
1991) as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, you will find it at
http://www.gnu.org/licenses/gpl.html, or write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110,
USA.

Should a provision of no. 9 and 10 of the GNU General Public License
be invalid or become invalid, a valid provision is deemed to have been
agreed upon which comes closest to what the parties intended
commercially. In any case guarantee/warranty shall be limited to gross
negligent actions or intended actions or fraudulent concealment.
"""

import math
import sys
import SequiturTool
from sequitur import Translator
from misc import gOpenIn, gOpenOut, set
import codecs
import re


# ===========================================================================
def loadPlainSample(fname, encoding=None):
    sample = []
    for line in gOpenIn(fname, encoding or defaultEncoding):
        fields = line.split()
        if not fields:
            continue
        left = tuple(fields[0])
        right = tuple(fields[1:])
        sample.append((left, right))
    return sample


def pronunciationsFromXmlLexicon(xml):
    pronunciations = {}
    lexicon = xml.getroot()
    for lemma in lexicon.getiterator("lemma"):
        orth = [
            orth.text.strip() for orth in lemma.findall("orth") if orth.text is not None
        ]
        phon = [tuple((phon.text or "").split()) for phon in lemma.findall("phon")]
        for w in orth:
            if w in pronunciations:
                pronunciations[w] += phon
            else:
                pronunciations[w] = phon
    return pronunciations


def loadBlissLexicon(fname):
    from xml.etree.ElementTree import ElementTree

    xml = ElementTree(file=gOpenIn(fname))
    pronunciations = pronunciationsFromXmlLexicon(xml)
    result = [
        (orth, phon)
        for orth in pronunciations
        if not (orth.startswith("[") and orth.endswith("]"))
        for phon in pronunciations[orth]
    ]
    result.sort()
    return result


def loadG2PSample(fname):
    if fname == "-":
        sample = loadPlainSample(fname)
    else:
        firstLine = gOpenIn(fname, defaultEncoding).readline()
        if firstLine.startswith("<?xml"):
            sample = [
                (tuple(orth), tuple(phon)) for orth, phon in loadBlissLexicon(fname)
            ]
        else:
            sample = loadPlainSample(fname)
    return sample


def loadP2PSample(compfname):
    fnames = compfname.split(":")
    assert len(fnames) == 2
    left = dict(loadG2PSample(fnames[0]))
    right = dict(loadG2PSample(fnames[1]))
    sample = []
    for w in set(left.keys()) & set(right.keys()):
        sample.append((left[w], right[w]))
    return sample


# ===========================================================================
def readApply(fname, encoding=None):
    for line in gOpenIn(fname, encoding):
        word = line.strip()
        left = tuple(word)
        yield word, left


def readApplySentences(fname, encoding=None):
    """Read sentences from a file and yield (word, graphemes, sentence) tuples for each word."""
    # Keep track of line number to handle duplicate lines
    line_num = 0
    total_words = 0
    empty_lines = 0
    
    try:
        for line in gOpenIn(fname, encoding):
            line_num += 1
            try:
                sentence = line.strip()
                
                if not sentence:  # Skip empty lines
                    empty_lines += 1
                    continue
                    
                # Generate a unique sentence ID that includes line number
                # This ensures each line is processed independently
                sentence_id = f"{line_num}:{sentence}"
                
                # Very simple word tokenization - adjust if needed
                words = sentence.split()
                if not words:
                    print(f"WARNING: Line {line_num} contains no words after tokenization: '{sentence}'", file=stderr)
                    continue
                    
                total_words += len(words)
                for word in words:
                    # Process each word
                    try:
                        left = tuple(word)
                        yield word, left, sentence_id
                    except Exception as e:
                        print(f"ERROR: Failed to process word '{word}' in line {line_num}: {str(e)}", file=stderr)
            except Exception as e:
                print(f"ERROR: Failed to process line {line_num}: {str(e)}", file=stderr)
                
        print(f"INFO: Processed {line_num} lines total ({empty_lines} empty lines skipped) with {total_words} words", file=stderr)
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to read input file '{fname}': {str(e)}", file=stderr)
        import traceback
        traceback.print_exc(file=stderr)
        # Yield nothing in case of file error


def readApplyP2P(fname, encoding=None):
    for line in gOpenIn(fname, encoding):
        fields = line.split()
        word = fields[0]
        left = tuple(fields[1:])
        yield word, left


def readApplyP2G(fname, encoding=None):
    for line in gOpenIn(fname, encoding):
        line = line.rstrip()
        fields = line.split("\t")
        if len(fields) == 1:
            word = fields[0]
            left = tuple(fields[0].split())
        elif len(fields) == 2:
            word = fields[0]
            left = tuple(fields[1].split())
        else:
            print("unknown format in file: %s" % (line), file=stderr)

        yield word, left


# ===========================================================================
class MemoryTranslator:
    def __init__(self, sample):
        self.memory = dict(sample)

    TranslationFailure = Translator.TranslationFailure

    def __call__(self, left):
        if left in self.memory:
            return self.memory[left]
        else:
            raise self.TranslationFailure()

    def reportStats(self, f):
        pass


# ===========================================================================
def mainTest(translator, testSample, options, output_file):
    if options.shouldTranspose:
        testSample = SequiturTool.transposeSample(testSample)
    if options.testResult:
        resultFile = gOpenOut(options.testResult, defaultEncoding)
    else:
        resultFile = None
    from Evaluation import Evaluator

    evaluator = Evaluator()
    evaluator.setSample(testSample)
    evaluator.resultFile = resultFile
    evaluator.verboseLog = output_file
    if options.test_segmental:
        supraSegmental = set([".", "'", '"'])

        def removeSupraSegmental(phon):
            return filter(lambda p: p not in supraSegmental, phon)

        evaluator.compareFilter = removeSupraSegmental
    result = evaluator.evaluate(translator)
    print(result)


def mainApply(translator, options, output_file):
    # Initialize counters for error tracking and verification
    input_line_count = 0
    output_line_count = 0
    error_count = 0
    processing_stats = {'total_words': 0, 'successful_words': 0, 'failed_words': 0}
    
    # Dictionary to store transcriptions by sentence
    sentence_transcriptions = {}
    # Keep track of current sentence for words in the same sentence
    current_sentence = None
    # Track processed sentences to avoid duplicates in output
    processed_sentences = set()
    
    try:
        # Count the number of lines in the input file
        try:
            with gOpenIn(options.applySample, options.encoding) as f:
                for line in f:
                    if line.strip():  # Skip empty lines in count
                        input_line_count += 1
            print(f"INFO: Input file contains {input_line_count} non-empty lines", file=stderr)
        except Exception as e:
            print(f"ERROR: Failed to count input lines: {str(e)}", file=stderr)
            input_line_count = 0  # Set to 0 to indicate failure
        
        if options.phoneme_to_phoneme:
            words = readApplyP2P(options.applySample, options.encoding)
        elif options.shouldTranspose:
            words = readApplyP2G(options.applySample, options.encoding)
        else:
            words = readApplySentences(options.applySample, options.encoding)

        if options.variants_mass or options.variants_number:
            wantVariants = True
            threshold = options.variants_mass or 1.0
            nVariantsLimit = options.variants_number or 1e9
        else:
            wantVariants = False
            
        # Process each item from the input
        for item in words:
            if len(item) == 3:  # Process as sentence
                word, left, sentence = item
                if sentence != current_sentence:
                    # If we're starting a new sentence, output the previous one
                    if current_sentence and current_sentence in sentence_transcriptions and current_sentence not in processed_sentences:
                        separator = options.sentence_separator
                        # Extract the original sentence text (remove line number prefix)
                        original_sentence = current_sentence.split(':', 1)[1]
                        phoneme_sequence = separator.join([phoneme for _, phoneme in sentence_transcriptions[current_sentence]])
                        print(("%s\t%s" % (original_sentence, phoneme_sequence)), file=output_file)
                        output_line_count += 1
                        # Mark this sentence as processed
                        processed_sentences.add(current_sentence)
                    # Start tracking new sentence
                    current_sentence = sentence
                    if sentence not in sentence_transcriptions:
                        sentence_transcriptions[sentence] = []
            else:  # Process as single word
                word, left = item
                sentence = None

            try:
                if wantVariants:
                    totalPosterior = 0.0
                    nVariants = 0
                    nBest = translator.nBestInit(left)
                    while totalPosterior < threshold and nVariants < nVariantsLimit:
                        try:
                            logLik, result = translator.nBestNext(nBest)
                        except StopIteration:
                            break
                        posterior = math.exp(logLik - nBest.logLikTotal)
                        result_str = " ".join(result)
                        
                        if sentence and nVariants == 0:
                            # Store for sentence output (first variant only)
                            sentence_transcriptions[sentence].append((word, result_str))
                        elif not sentence:
                            # Normal variant output for single word
                            print(
                                (
                                    "%s\t%d\t%f\t%s"
                                    % (word, nVariants, posterior, result_str)
                                ),
                                file=output_file,
                            )
                        
                        totalPosterior += posterior
                        nVariants += 1
                else:
                    processing_stats['total_words'] += 1
                    result = translator(left)
                    result_str = " ".join(result)
                    processing_stats['successful_words'] += 1
                    
                    if sentence:
                        # Store for sentence output
                        sentence_transcriptions[sentence].append((word, result_str))
                    else:
                        # Output single word immediately
                        print(("%s\t%s" % (word, result_str)), file=output_file)
                        output_line_count += 1
            except translator.TranslationFailure:
                exc = sys.exc_info()[1]
                error_count += 1
                processing_stats['failed_words'] += 1
                try:
                    print('ERROR: Failed to convert "%s": %s' % (word, exc), file=stderr)
                except:
                    pass

        # Output the final sentence if there is one and it hasn't been processed yet
        if current_sentence and current_sentence in sentence_transcriptions and current_sentence not in processed_sentences:
            separator = options.sentence_separator
            # Extract the original sentence text (remove line number prefix)
            original_sentence = current_sentence.split(':', 1)[1]
            phoneme_sequence = separator.join([phoneme for _, phoneme in sentence_transcriptions[current_sentence]])
            print(("%s\t%s" % (original_sentence, phoneme_sequence)), file=output_file)
            output_line_count += 1
            
        # Print final statistics
        print(f"\nProcessing Summary:", file=stderr)
        print(f"  Input lines: {input_line_count}", file=stderr)
        print(f"  Output lines: {output_line_count}", file=stderr)
        print(f"  Total words processed: {processing_stats['total_words']}", file=stderr)
        print(f"  Successfully converted words: {processing_stats['successful_words']}", file=stderr)
        print(f"  Failed conversions: {processing_stats['failed_words']}", file=stderr)
        print(f"  Total errors: {error_count}", file=stderr)
        
        # Check if input and output line counts match
        if input_line_count > 0 and input_line_count != output_line_count:
            print(f"WARNING: Input line count ({input_line_count}) does not match output line count ({output_line_count})!", file=stderr)
        elif input_line_count > 0:
            print(f"SUCCESS: Input and output line counts match ({input_line_count} lines).", file=stderr)
    
    except Exception as e:
        print(f"CRITICAL ERROR during processing: {str(e)}", file=stderr)
        import traceback
        traceback.print_exc(file=stderr)


def mainApplyWord(translator, options, output_file):
    word = options.applyWord
    
    try:
        if options.shouldTranspose:
            left = tuple(word.split())
        else:
            left = tuple(word)

        print(f"INFO: Attempting to convert word: {word}", file=stderr)
        
        try:
            result = translator(left)
            print(("%s\t%s" % (word, " ".join(result))), file=output_file)
            print(f"SUCCESS: Converted word: {word}", file=stderr)
        except translator.TranslationFailure:
            exc = sys.exc_info()[1]
            try:
                print(f'ERROR: Failed to convert "{word}": {exc}', file=stderr)
            except:
                print(f'ERROR: Failed to convert "{word}" (could not print detailed error)', file=stderr)
    except Exception as e:
        print(f"CRITICAL ERROR processing word '{word}': {str(e)}", file=stderr)
        import traceback
        traceback.print_exc(file=stderr)


def main(options, args):
    import locale

    if options.phoneme_to_phoneme:
        loadSample = loadP2PSample
    else:
        loadSample = loadG2PSample

    enc = locale.getpreferredencoding()
    if hasattr(sys.stdout, "buffer"):
        log_stdout = codecs.getwriter(enc)(sys.stdout.buffer, errors="backslashreplace")
    else:
        log_stdout = codecs.getwriter(enc)(sys.stdout, errors="backslashreplace")

    if hasattr(sys.stderr, "buffer"):
        log_stderr = codecs.getwriter(enc)(sys.stderr.buffer, errors="backslashreplace")
    else:
        log_stderr = codecs.getwriter(enc)(sys.stderr, errors="backslashreplace")

    if options.fakeTranslator:
        translator = MemoryTranslator(loadSample(options.fakeTranslator))
    else:
        model = SequiturTool.procureModel(options, loadSample, log=log_stdout)
        if not model:
            return 1
        if options.testSample or options.applySample or options.applyWord:
            translator = Translator(model)
            if options.stack_limit:
                translator.setStackLimit(options.stack_limit)
        del model

    if options.testSample:
        mainTest(translator, loadSample(options.testSample), options, log_stdout)
        translator.reportStats(log_stdout)

    if options.applySample:
        mainApply(
            translator, options, gOpenOut("-", options.encoding or defaultEncoding)
        )
        translator.reportStats(log_stderr)

    if options.applyWord:
        mainApplyWord(translator, options, log_stdout)


# ===========================================================================
if __name__ == "__main__":
    import optparse
    import tool

    optparser = optparse.OptionParser(
        usage="%prog [OPTION]... FILE...\n" + str(__doc__),
        version="%prog " + __version__,
    )
    tool.addOptions(optparser)
    SequiturTool.addTrainOptions(optparser)
    optparser.add_option(
        "-e",
        "--encoding",
        default="ISO-8859-15",
        help="use character set encoding ENC",
        metavar="ENC",
    )
    optparser.add_option(
        "-P",
        "--phoneme-to-phoneme",
        action="store_true",
        help="train/apply a phoneme-to-phoneme converter",
    )
    optparser.add_option(
        "--test-segmental",
        action="store_true",
        help="evaluate only at segmental level, i.e. do not count "
        "syllable boundaries and stress marks",
    )
    optparser.add_option(
        "-B",
        "--result",
        dest="testResult",
        help="store test result in table FILE (for use with bootlog or R)",
        metavar="FILE",
    )
    optparser.add_option(
        "-a",
        "--apply",
        dest="applySample",
        help="apply grapheme-to-phoneme conversion to words read from FILE",
        metavar="FILE",
    )
    optparser.add_option(
        "-w",
        "--word",
        dest="applyWord",
        help="apply grapheme-to-phoneme conversion to word",
        metavar="string",
    )
    optparser.add_option(
        "-V",
        "--variants-mass",
        type="float",
        help="generate pronunciation variants until \\sum_i p(var_i) >= Q "
        "(only effective with --apply)",
        metavar="Q",
    )
    optparser.add_option(
        "--variants-number",
        type="int",
        help="generate up to N pronunciation variants (only effective with --apply)",
        metavar="N",
    )
    optparser.add_option(
        "-f",
        "--fake",
        dest="fakeTranslator",
        help="use a translation memory (read from sample FILE) instead of a genuine"
        " model (use in combination with -x to evaluate two files against each other)",
        metavar="FILE",
    )
    optparser.add_option(
        "--stack-limit",
        type="int",
        help="limit size of search stack to N elements",
        metavar="N",
    )
    optparser.add_option(
        "--sentence-separator",
        default=" # ",
        help="separator between word transcriptions in sentences (default: ' # ')",
        metavar="SEP",
    )

    try:
        options, args = optparser.parse_args()

        global stdout, stderr, defaultEncoding
        if sys.version_info[:2] <= (2, 5):
            global defaultEncoding
            defaultEncoding = options.encoding
            encoder, decoder, streamReader, streamWriter = codecs.lookup(options.encoding)
            stdout = streamWriter(sys.stdout)
            stderr = streamWriter(sys.stderr)
        else:
            defaultEncoding = options.encoding
            stdout = sys.stdout
            stderr = sys.stderr

        # Print startup information with file encoding
        print(f"INFO: Starting g2p_sentences.py using encoding: {options.encoding}", file=stderr)
        if options.applySample:
            print(f"INFO: Will process input file: {options.applySample}", file=stderr)
        elif options.applyWord:
            print(f"INFO: Will process single word: {options.applyWord}", file=stderr)
            
        # Run the main function with proper error handling
        exit_code = tool.run(main, options, args)
        
        # Final status message
        if exit_code == 0:
            print("INFO: Processing completed successfully", file=stderr)
        else:
            print(f"WARNING: Processing completed with exit code {exit_code}", file=stderr)
            
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"CRITICAL ERROR: Unhandled exception in main program: {str(e)}", file=stderr)
        import traceback
        traceback.print_exc(file=stderr)
        sys.exit(1)