# *-* coding: utf-8 *-*
# @version: Python 2.7
import unittest
import binary
import os
import app

class TestCompressionLZW(unittest.TestCase):

	def setUp(self):
		self.bitlen = 9
		self.seq = [self.bitlen, 16, 101, 115, 116, 257, 179, 256, 18, 39]

	def test_write_seq(self):
		round = lambda x:x if x % 8 == 0 else x + 8 - x % 8
		with open('tests/b.bin', 'wb') as f:
			binary.write_seq(self.seq, f)

		must_be_size = 1+round(len(self.seq)*self.bitlen)/8

		real_size = os.stat('tests/b.bin').st_size

		self.assertEqual(must_be_size, real_size)

	def test_read_seq(self):
		with open('tests/b.bin', 'rb') as f:
			extracted = binary.read_seq(f)

		self.seq.pop(0)
		self.assertListEqual(self.seq, extracted)

	def test_bitlen(self):
		self.assertLess(max(self.seq), 2**self.bitlen, (
			"Test failed ! Impossible de coder {} sur {} bits!".format(
				[el for el in self.seq if el >= 2**self.bitlen], 
				self.bitlen)
			)
		)

	def test_file_compress(self):
		app.file_compress('tests/lorem.txt', 'tests/lorem.lzw')

		initial_size = os.stat('tests/lorem.txt').st_size
		compressed_size = os.stat('tests/lorem.lzw').st_size

		self.assertLess(compressed_size, initial_size)

	def test_file_decompress(self):
		with open('tests/lorem.txt') as f:
			initial_lorem = f.read()

		app.file_decompress('tests/lorem.lzw', 'tests/t_lorem.txt')
		with open('tests/t_lorem.txt') as f:
			decompressed_lorem = f.read()

		self.assertEqual(initial_lorem, decompressed_lorem)

	def test_raw_compress_decompress(self):
		text = "Les chaussettes de l'archiduchesse sont elle sèches archi sèches äÆ○╣"
		compressed = app.raw_compress(text)
		compressed.pop(0)
		decompressed = app.raw_decompress(compressed)
		
		self.assertEqual(text, decompressed)

if __name__ == '__main__':
	missing = []
	for file in ('b.bin', 'lorem.lzw', 'lorem.txt'):
		if not os.path.isfile('tests/' + file):
			missing.append(file)
	if missing != []:
		print "Les fichiers {} sont nécessaires aux tests".format(
			['tests/%s' % el for el in missing])
	else:
		unittest.main()

