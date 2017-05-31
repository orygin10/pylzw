# -*- coding: utf-8 -*-
from cStringIO import StringIO
import struct
import math
import pickle

def write_int_frame(n, f):
	"""
	@param n: Integer to write to file
	@type n: int
	@param f: File handle
	@summary: Writes integer to binary file in a frame [nul]|[integer bytes]
	"""
	chunkSize = lambda bitarray:int(math.ceil(len(bitarray)/8.0))*8 # Get real byte size from bits

	b = bin(n)[2:] 				   # Convert n to binary
	s = b.rjust(chunkSize(b), '0') # Pad with zeroes on the left

	sio = StringIO(s)

	f.write(chr(255)) 		# Write [nul]
	byte = sio.read(8) 		# Grab first 8 bits

	while byte: 			# For each byte
		i = int(byte, 2) 	# Convert to int 
		c = chr(i) 			# Convert to char
		f.write(c) 			# Write byte to file
		byte = sio.read(8) 	# Grab next 8 bits



def write_char_frame(c, f):
	"""
	@param c: Single byte
	@type c: str
	@param f: file handle
	@summary: writes [nul]|[byte] to file
	"""
	f.write(chr(255)) # Write [nul]
	f.write(c)		# Write byte


def serialize(l, filename):
	"""
	@param l: Text to serialize
	@type l: str/int list
	@summary: Serialize hybrid list"""
	with open(filename, 'wb') as f:
		for el in l:
			if isinstance(el, str):		# If single byte
				write_char_frame(el, f) # Write byte Frame
			elif isinstance(el, int): 	# If int (multi-bytes)
				write_int_frame(el, f)	# Write int Frame
			else:
				raise SystemExit("Erreur avec {}".format(c))

def byteToBits(byte):
	"""
	@param byte: byte to convert
	@type byte: len-1 str
	@summary: Convert byte to bits
	@rtype: str
	"""
	i = ord(byte)				# Convert byte to int
	bits = bin(i)[2:]			# Convert int to bits
	return bits.rjust(8, '0')	# Pad with zeroes on the left

def unserialize(filename):
	"""
	@param filename: Name of the file to unserialize
	@type filename: str
	@summary: Read file and parse binary data
	@rtype: list
	"""
	unserialized = []
	with open(filename, 'rb') as f:
		content = f.read() 				 # Read all serialized content

	binlist = content.split(chr(255))[1:] 	 # Unpack serialized content on [nul] separator
	for el in binlist:
		if len(el)==1: 					 # If single char
			unserialized.append(el) 	 # Append to the final result
		else:							 # If multi-bytes int
			sio = StringIO(el)
			bits = ''
			byte = sio.read(1) 			 # Grab a byte
			while byte:					 # For each byte in element
				bits += byteToBits(byte) # Convert to bits
				byte = sio.read(1)		 # Grab next byte
			if bits:
				i = int(bits, 2)		 # Convert to int
				unserialized.append(i) 	 # Append to the final result
	print binlist
	return unserialized

def tests():
	entier = 51256
	# Integer frame
	with open('tests/intframe.bin', 'wb') as f:
		write_int_frame(entier, f)
	
	# Serialize
	l = ['s', 'a', 'l', 'u', 't', ' ', 94020, 333]
	print "Liste initiale     : {}".format(l)
	serialize(l, 'tests/serialized.bin')

	# Unserialize
	final = unserialize('tests/serialized.bin')
	print "Liste unserialized : {}".format(final)


if __name__ == "__main__":
	tests()