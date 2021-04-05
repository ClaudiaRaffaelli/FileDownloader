import math


def size_converter(size_bytes):
	# converts input size in bytes in a more readable unit
	if (size_bytes == 0) or (size_bytes is None):
		return "0B"
	size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return str(s) + " " + size_name[i]


def speed_calculator(size_bytes, time_interval):
	return size_converter(size_bytes // time_interval) + "/s"


class CustomRole:
	# class that holds all the custom roles used by the two table model
	full_path = 0
	url = 1
	progress_bar = 2
	plain_dimension = 3
	start_time = 4
	end_time = 5
	plain_downloaded_size = 6
