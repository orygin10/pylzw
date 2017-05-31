# *-* coding: utf-8 *-*
# @version: Python 2.7
from cStringIO import StringIO
import sys

def write_seq(seq, hFile):
	"""
	@summary: Write sequence to binary file
	@param seq: Compressed sequence
	@type seq: list(int)
	@param hFile: File handle (wb)
	@note: All elements of seq must be ints
	"""
	bitlen = seq.pop(0)				# Grab encoding size
	if bitlen > 255:				# Encoding size must be converted to byte
		raise ValueError("La taille du dictionnaire dépasse 2^255")

	hFile.write(chr(bitlen))		# Write encoding size in header

	bits = ''						# Sequence of bits
	for code in seq:				# For each integer
		b = bin(code)[2:]			# convert to binary
		b = b.rjust(bitlen, '0')	# if less than 8 bits, pad with zeroes on the left
		bits += b 					# Append to sequence of bits

	sio = StringIO(bits)			# Emulate file handle from string (sequence of bits)
	byte = sio.read(8)				# Grab 8 bits (8 chars)
	while byte:						# for each pack of 8 bits
		byte = byte.ljust(8, '0')	# if less than 8 bits, ajust with zeroes on the right
		i = int(byte, 2)			# convert to integer
		hFile.write(chr(i))			# write binary value to file
		byte = sio.read(8)			# grab next byte

def read_seq(hFile):
	"""
	@summary: Extract sequence from file\
	First element is encoding size\
		aka. bitlen\
		aka. dict size binary length
	@param hFile: File handle(rb)
	@return: Extracted sequence
	@rtype: list(int)
	"""
	bits = ''						# Sequence of bits

	bitlen = ord(hFile.read(1))		# Grab header in first byte
	byte = hFile.read(1)			# Grab first byte in file body
	while byte:						# for each byte
		i = ord(byte)				# convert to integer
		b = bin(i)[2:]				# convert to binary
		b = b.rjust(8, '0')			# ajust to 8 bits with zeroes on the left
		bits += b 					# append to sequence of bits
		byte = hFile.read(1)		# grab next byte

	seq = []						# code sequence
	sio = StringIO(bits)			# emulate file handle from string
	s = sio.read(bitlen)			# read first chunk of lenght bitlen
	while s and len(s)==bitlen:		# for each chunk or until chunk size is less than bitlen
		seq.append(int(s, 2))		# append code to code sequence
		s = sio.read(bitlen)		# grab next chunk
	return seq

def dump(seq, hFile):
	"""
	@summary: Higher level write_seq, converts all chars to ints
	@param seq: Compressed sequence
	@type seq: list(int~str)
	@param hFile: File handle (wb)"""
	seq = [ord(el) if isinstance(el, str) else el for el in seq]
	write_seq(seq, hFile)

def load(hFile):
	"""
	@summary: Higher level read_seq, convert all ascii ints to chars
	@param hFile: File handle (rb)
	@return: Extracted sequence
	@rtype: list(int~str)
	"""
	seq = read_seq(hFile)
	return [chr(el) if el<=255 else el for el in seq]