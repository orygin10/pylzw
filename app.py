# *-* coding: utf-8 *-*
# @version: Python 2.7
from getopt import getopt, GetoptError
from timeit import default_timer as timer
import sys
import os
import binary # My module


def raw_compress(uncompressed):
    """
    @summary: Compress a string to a list of output symbols.
    @param uncompressed: data not yet compressed
    @type uncompressed: str
    @return: hybrid list, elements of type int or str
    @rtype: list
    @note: First element is encoding size in bits
    @warn: xrange is python 2-only, use range for Python 3
    """

    # Prologue 
    verboseprint("Compression starting.")
    top = timer()
    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))

    w = ""
    result = []

    # Body
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    # Output the code for w.
    if w:
        result.append(dictionary[w])
    
    # Epilogue
    end = timer()
    duration = end-top
    verboseprint("Compression completed in %.2f seconds" % duration)
    if duration < 0.01:
        verboseprint("Try with a bigger file like [tests/bible.txt] for a more comprehensive duration")

    ints = [el for el in result if isinstance(el, int)] # Extract ints from result
    bitlen = len(bin(max(ints))[2:]) # Number of bits needed to encode highest dictionary entry
    result.insert(0, bitlen) # First element of result is bitlen

    verboseprint("\n<<< Compression data >>>")
    verboseprint("Algorithm efficiency :")
    verboseprint("\t%d chars (bytes) to compress" % len(uncompressed))
    verboseprint("\t%d compressed elements" % len(result))
    verboseprint("\nMetrics for binary encoding :")
    verboseprint("\tHighest value in dictionary : %d" % max(ints))
    verboseprint("\tEncoding size : %d bits" % bitlen)

    return result


def raw_decompress(compressed):
    """
    @summary: Use LZW Algorithm to reverse compression
    @param compressed: compressed data
    @type compressed: list
    @return: uncompressed data
    @rtype: str
    """

    # Prologue
    verboseprint("Decompression starting")
    top = timer()
    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))

    # Body
    w = result = compressed.pop(0)
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed k: %s' % k)
        result += entry

        # Add w+entry[0] to the dictionary.
        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        w = entry

    # Epilogue
    end = timer()
    duration = end-top
    verboseprint("Decompression completed in %.2f seconds" % duration)
    return result

def ratios(plaintext, compressed):
    """
    @param plaintext: Uncompressed file name
    @param compressed: Compressed file name
    @summary: Print both compression ratio definition
    """
    verboseprint("\n<<< Compression results >>>")
    size_pt = os.stat(plaintext).st_size
    size_c = os.stat(compressed).st_size

    verboseprint("Size :")
    verboseprint("\t%s : %d B\n\t%s : %d B" % 
        (plaintext, size_pt, compressed, size_c)
    )

    ratioA = float(size_pt) / float(size_c)     # Compression ratio : uncompressed size / compressed size
    ratioB = 1-(float(size_c) / float(size_pt)) # Space savings : 1 - (compressed size / uncompressed size)

    verboseprint("Ratios :")
    verboseprint("\tCompression ratio : %.2f:1" % ratioA )
    verboseprint("\tSpace savings : %d%%" % int(ratioB*100) )

def file_compress(filename_in, filename_out):
    """
    @param filename_in: File to compress
    @param filename_out: Future compressed file
    @summary: LZW File compression
    @rtype: None
    """
    with open(filename_in, 'r') as file_in:
        raw_data = file_in.read()
        compressed_data = raw_compress(raw_data)
        with open(filename_out, 'wb') as f:
            binary.dump(compressed_data, f)

    ratios(filename_in, filename_out)


def file_decompress(filename_in, filename_out):
    """
    @param filename_in: File to decompress
    @param filename_out: Future decompressed file
    @summary: LZW File decompression
    @rtype: None
    """
    with open(filename_in, 'rb') as f:
        compressed_data = binary.load(f)

    with open(filename_out, 'w') as file_out:
        raw_data = raw_decompress(compressed_data)
        file_out.write(raw_data)

def main(argv):
    """
    @summary: Execute operation based on command line argument
    @param argv: Command line arguments
    @rtype: None
    """
    if not 0 < len(argv) <= 3:
        usage("Nombre d'arguments")
        return 2

    global VERBOSE
    chunk_size = 0
    operation = None
    operation_args = None

    try:
        opts, args = getopt(
            argv, "hc:d:v", ["help", "compress=", "decompress=", "verbose"])
    except GetoptError:
        usage("Erreur getopt")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            operation = usage
            operation_args = ["Aide"]

        elif opt in ("-c", "--compress"):
            if not os.path.isfile(arg):
                raise IOError("Erreur, %s n'est pas un fichier valide" % arg)
            operation = file_compress
            operation_args = (arg, args[0])

        elif opt in ("-d", "--decompress"):
            if not os.path.isfile(arg):
                raise IOError("Erreur, %s n'est pas un fichier valide" % arg)
            operation = file_decompress
            operation_args = (arg, args[0])

        elif opt in ('-v', '--verbose'):
            VERBOSE = True

        else:
            usage("Mauvais paramètre : %s" % opt)

    verboseprint("Args : {}".format(argv))
    if operation_args:
        operation(*operation_args)
    else:
        operation()

    return 0

def verboseprint(*args):
    """
    @summary: Print message if verbose is enabled, otherwise do nothing
    @param args: Message(s) to print
    @type args: str or iter(str)
    @rtype: None
    """
    if not VERBOSE:
        return
    else:
        for arg in args:
            print arg

def usage(msg=""):
    """
    @summary: Prints usage info
    @param msg: facultative message to print before usage info
    @type msg: str
    @rtype: None
    """
    if msg:
        print msg
    print(
"""Usage :
python app.py [OPTIONS] [FILE]
-c, --compress : File to compress
-d, --decompress : File to decompress
-h, --help : Print this message
-v, --verbose : Verbose mode

To launch unit tests = python tests.py
""")


VERBOSE = False
if __name__ == "__main__":
    # Exit with main() return value
    sys.exit(main(sys.argv[1:]))
