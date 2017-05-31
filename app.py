# *-* coding: utf-8 *-*
# @version: Python 2.7
import sys
import os
from getopt import getopt, GetoptError
import binary

def raw_compress(uncompressed):
    """
    @summary: Compress a string to a list of output symbols.
    @param uncompressed: data not yet compressed
    @type uncompressed: str
    @return: hybrid list, elements of type int or str
    @rtype: list
    @note: First element is encoding size in bits
    """

    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))

    w = ""
    result = []

    verboseprint("%d uncompressed chars" % len(uncompressed))
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
    verboseprint("%d compressed elements" % len(result))
    ints = [el for el in result if isinstance(el, int)]
    verboseprint("Taille max : %d" % max(ints))

    bitlen = len(bin(max(ints))[2:])
    verboseprint("Encoding size = %d bits" % bitlen)
    result.insert(0, bitlen)
    return result


def raw_decompress(compressed):
    """
    @summary: Decompress a list of output ks to a string.
    @param compressed: compressed data
    @type compressed: list
    @return: uncompressed data
    @rtype: str
    """

    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), chr(i)) for i in xrange(dict_size))

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
    return result

def file_compress(filename_in, filename_out):
    """
    @param filename_in: File to compress
    @param filename_out: Future compressed file
    @summary: LZW File compression
    """
    with open(filename_in, 'r') as file_in:
        raw_data = file_in.read()
        compressed_data = raw_compress(raw_data)
        with open(filename_out, 'wb') as f:
            binary.dump(compressed_data, f)


def file_decompress(filename_in, filename_out):
    """
    @param filename_in: File to decompress
    @param filename_out: Future decompressed file
    @summary: LZW File decompression 
    """
    with open(filename_out, 'w') as file_out:
        with open(filename_in, 'rb') as f:
            compressed_data = binary.load(f)
        raw_data = raw_decompress(compressed_data)
        file_out.write(raw_data)


def main(argv):
    """Handle opt and argv"""
    if not 0 < len(argv) <= 3:
        usage("Nombre d'arguments")
        sys.exit(2)

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

    verboseprint(opts)
    if operation_args:
        operation(*operation_args)
    else:
        operation()


def verboseprint(*args):
    """Print message if verbose is enabled, otherwise do nothing"""
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
    sys.exit(main(sys.argv[1:]))
