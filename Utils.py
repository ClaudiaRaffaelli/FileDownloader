import math


def size_converter(size_bytes):
	# converts input size in bytes in a more readable unit
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return str(s) + " " + size_name[i]

