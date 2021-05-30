from __future__ import division
import sys
import numpy as np
import OpenEXR as exr
import Imath
from PIL import Image

import struct

def packFloatInto8BitVec2(v, min, max):
	zeroToOne = (v - min) / (max - min)
	zeroTo16Bit = zeroToOne * 256.0 * 255.0
	val1 = zeroTo16Bit % 256.0
	val2 = zeroTo16Bit / 256.0
	return val1, val2

def extractDataFromChannel(numberOfChannelsToHandle, original_size, exr_channel1, exr_channel2):
	print('original_size[1]: ' + str(original_size[1]))
	print('original_size[0]: ' + str(original_size[0]))
	pos = int(original_size[1] / 2)
	print('pos: ' + str(pos))
	print('exr_channel[0]: ' + str(exr_channel1[0]))
	print('exr_channel[1]: ' + str(exr_channel1[1]))
	print('exr_channel[2]: ' + str(exr_channel1[2]))
	print('exr_channel[3]: ' + str(exr_channel1[3]))
	fourChannelImg = np.zeros((original_size[1], original_size[0], 4)).astype(int)

	i_x = 0
	i_y = 0

	exr_channel1.shape = (original_size[1], original_size[0])
	exr_channel2.shape = (original_size[1], original_size[0])

	while i_y < original_size[1]:
		while i_x < original_size[0]:
			R_origin = exr_channel1[i_y][i_x]
			G_origin = exr_channel2[i_y][i_x]
			#print('R_origin: ' + str(R_origin))
			#print('G_origin: ' + str(G_origin))	
			val11,val12 = packFloatInto8BitVec2(R_origin,0,1)
			val21,val22 = packFloatInto8BitVec2(G_origin,0,1)
			for i in (0, 1, 2, 3):				
				if (i == 0):
					# R channel
					fourChannelImg[i_y, i_x, 0] = val11
				if (i == 1):
					#G channel
					fourChannelImg[i_y, i_x, 1] = val12
				if (i == 2):
					#B channel
					if(numberOfChannelsToHandle == '-double'):
						fourChannelImg[i_y, i_x, 2] = val21
					else:
						fourChannelImg[i_y, i_x, 2] = 0
				if (i == 3):
					#A channel
					if(numberOfChannelsToHandle == '-double'):
						fourChannelImg[i_y, i_x, 3] = val22
					else:
						fourChannelImg[i_y, i_x, 3] = 0
			i_x = i_x + 1
		i_y = i_y + 1
		i_x = 0

	return Image.fromarray(np.uint8(fourChannelImg))


def unpack(numberOfChannelsToHandle, filename, png_filename):
	exrFile = exr.InputFile(filename)
	header = exrFile.header()
	print('Header compression : ' + str(header['compression']))
	print('Header channels : ' + str(header['channels']))
	dw = header['dataWindow']
	pt = Imath.PixelType(Imath.PixelType.HALF)
	size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
	#print('Size of output image: ' + size)

	if(sys.argv[1] == '-double'):
		cc_r = np.fromstring(exrFile.channel('R', pt), dtype=np.float16)
		cc_g = np.fromstring(exrFile.channel('G', pt), dtype=np.float16)
		
		RG = extractDataFromChannel(numberOfChannelsToHandle, size, cc_r, cc_g)

		RG.save(png_filename.replace(".png", "_RGBA.png"))
		
	if(sys.argv[1] == '-single'):
		cc_r = np.fromstring(exrFile.channel('Y', pt), dtype=np.float16)
		cc_g = np.zeros((size[1], size[0], 1)).astype(np.float16)

		RG = extractDataFromChannel(numberOfChannelsToHandle, size, cc_r, cc_g)

		RG.save(png_filename.replace(".png", "_RGBA.png"))



def main(fpth):
	if(sys.argv[1] == '-single'):
		print('Unpack EXR: ' + sys.argv[1] + ' to file: ' + sys.argv[2] + ' as single channel EXR')
	if(sys.argv[1] == '-double'):
		print('Unpack EXR: ' + sys.argv[1] + ' to file: ' + sys.argv[2] + ' as double channels EXR')
	else:
		print('Error in program input')
	unpack(sys.argv[1], sys.argv[2], sys.argv[3])
	return


if __name__ == '__main__':
	main(sys.argv[1:])
