import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util


def LocalSsd():
	fn = "i2.xlarge-160425-011750-ami-1fc7d575-54.146.53.151"
	_GenLocalSsdData(fn)
	_PlotRandR4k(fn)
	_PlotRandR4kLog(fn)
	_PlotRandW4k(fn)
	_PlotRandW4kLog(fn)
	_PlotSeqW100m(fn)


def EbsSsd():
	# files are split into 2
	fn0 = "r3.xlarge-160422-220625-ami-1fc7d575-54.226.59.195"
	fn1 = "r3.xlarge-160423-195510-ami-1fc7d575-54.226.59.195"

	_GenEbsSsdData(fn0, fn1)
	_PlotRandR4k(fn1)
	_PlotRandR4kLog(fn1)
	_PlotRandW4k(fn1)
	_PlotRandW4kLog(fn1)
	_PlotSeqW100m(fn1)


def _GenLocalSsdData(fn):
	fn_plot_data = "plot-data/%s" % fn
	fn_raw = "../log/ioping/%s" % fn

	# Uncompress the raw files if not exist
	if not os.path.isfile(fn_raw):
		with Cons.MeasureTime("file %s doesn't exist. uncompressing from the archive" % fn_raw):
			cmd = "7z x -o../log/ioping %s.7z" % fn_raw
			Util.RunSubp(cmd)

	# Generate one if not exist. Skip for now. It's fast enough.
	#if os.path.isfile(fn_plot_data):
	#	Cons.P("%s already exists" % fn_plot_data)
	#	return

	if not os.path.exists("plot-data"):
		os.makedirs("plot-data")

	with Cons.MeasureTime("Generating plot data %s" % fn_plot_data):
		with open(fn_raw) as fo_r, open(fn_plot_data, "w") as fo_w:
			fmt = "%13s" \
					" %5.1f" \
					" %3d %3d %5d %4d" \
					" %3d %3d %5d %3d" \
					" %6d"
			fo_w.write("%s\n" % Util.BuildHeader(fmt,
				"datetime" \
				" blocks_used_percent" \
				" rr_4k_min rr_4k_avg rr_4k_max rr_4k_sd" \
				" rw_4k_min rw_4k_avg rw_4k_max rw_4k_sd" \
				" seqw_100m"
				))

			# 160425-011752
			# 100 17430 5737 23499713 170 174 211 5
			# 100 14822 6747 27634597 134 148 231 17
			# 1 216553 5 484212179 216553 216553 216553 0
			# Filesystem     1K-blocks    Used Available Use% Mounted on
			# /dev/xvda1       8115168 2545256   5134636  34% /
			# /dev/xvdb      769018760  173080 768829296   1% /mnt/local-ssd1

			i = 0
			dt = None
			block_used_percent_prev = None
			blocks_total = None
			blocks_used  = None
			rr_4k_min = None
			rr_4k_avg = None
			rr_4k_max = None
			rr_4k_sd  = None
			rw_4k_min = None
			rw_4k_avg = None
			rw_4k_max = None
			rw_4k_sd  = None
			seqw_100m = None
			for line in fo_r.readlines():
				#Cons.P(line)
				if i == 0:
					dt = line.strip()
				# 4k rand read
				elif i == 1:
					t = line.split()
					if len(t) != 8:
						raise RuntimeError("Unexpected format [%s]" % line)
					# All in us
					rr_4k_min = int(t[4])
					rr_4k_avg = int(t[5])
					rr_4k_max = int(t[6])
					rr_4k_sd  = int(t[7])
				elif i == 2:
					t = line.split()
					if len(t) != 8:
						raise RuntimeError("Unexpected format [%s]" % line)
					# All in us
					rw_4k_min = int(t[4])
					rw_4k_avg = int(t[5])
					rw_4k_max = int(t[6])
					rw_4k_sd  = int(t[7])
				elif i == 3:
					t = line.split()
					if len(t) != 8:
						raise RuntimeError("Unexpected format [%s]" % line)
					# All of the min, avg, max are the same since there is only 1 request
					# at a time.
					seqw_100m = int(t[4])
				elif i == 6:
					t = line.split()
					if (len(t) != 6) or (t[0] != "/dev/xvdb"):
						raise RuntimeError("Unexpected format [%s]" % line)
					blocks_total = int(t[1])
					blocks_used  = int(t[2])

				i += 1
				if i == 7:
					block_used_percent = round(100.0 * blocks_used / blocks_total, 1)
					if block_used_percent_prev != block_used_percent:
						fo_w.write((fmt + "\n") % (dt
							, (100.0 * blocks_used / blocks_total)
							, rr_4k_min, rr_4k_avg, rr_4k_max, rr_4k_sd
							, rw_4k_min, rw_4k_avg, rw_4k_max, rw_4k_sd
							, seqw_100m
							))
					block_used_percent_prev = block_used_percent
					i = 0
					dt = None
					blocks_total = None
					blocks_used  = None
					rr_4k_min = None
					rr_4k_avg = None
					rr_4k_max = None
					rr_4k_sd  = None
					rw_4k_min = None
					rw_4k_avg = None
					rw_4k_max = None
					rw_4k_sd  = None
					seqw_100m = None
		Cons.P("Created %s %d" % (fn_plot_data, os.path.getsize(fn_plot_data)))

			
def _PlotSeqW100m(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/seqw-100m-lat-%s.pdf" % fn

	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out

		Util.RunSubp("gnuplot %s/seqw-100m.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotRandR4k(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randr-4k-lat-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randr-4k.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotRandR4kLog(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randr-4k-lat-log-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randr-4k-log.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotRandW4k(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randw-4k-lat-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randw-4k.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotRandW4kLog(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randw-4k-lat-log-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randw-4k-log.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


###############################################################################

def _GenEbsSsdData(fn0, fn1):
	fn_plot_data = "plot-data/%s" % fn1
	fn_raw0 = "../log/ioping/%s" % fn0
	fn_raw1 = "../log/ioping/%s" % fn1

	# Generate one if not exist. Skip for now. It's fast enough.
	#if os.path.isfile(fn_plot_data):
	#	Cons.P("%s already exists" % fn_plot_data)
	#	return

	# Uncompress the raw files if not exist
	for fn in [fn_raw0, fn_raw1]:
		if not os.path.isfile(fn):
			with Cons.MeasureTime("file %s doesn't exist. uncompressing from the archive" % fn):
				cmd = "7z x -o../log/ioping %s.7z" % fn
				Util.RunSubp(cmd)

	if not os.path.exists("plot-data"):
		os.makedirs("plot-data")

	with Cons.MeasureTime("Generating plot data %s" % fn_plot_data):
		with open(fn_plot_data, "w") as fo_w, open(fn_raw0) as fo_r0, open(fn_raw1) as fo_r1:
			fmt = "%13s" \
					" %5.1f" \
					" %3d %4d %5d %4d" \
					" %3d %4d %5d %4d" \
					" %6d"
			fo_w.write("%s\n" % Util.BuildHeader(fmt,
				"datetime" \
				" blocks_used_percent" \
				" rr_4k_min rr_4k_avg rr_4k_max rr_4k_sd" \
				" rw_4k_min rw_4k_avg rw_4k_max rw_4k_sd" \
				" seqw_100m"
				))

			#160423-195525
			#100 68474 1460 5981833 230 685 1631 568
			#100 74883 1335 5469866 495 749 4723 585
			#1 1690975 1 62010142 1690975 1690975 1690975 0
			#Filesystem       1K-blocks       Used   Available Use% Mounted on
			#/dev/xvda1         8115168    2676196     5003696  35% /
			#/dev/xvdc      17111375772 1565491700 15545867688  10% /mnt/ebs-ssd1

			i = 0
			dt = None
			block_used_percent_prev = None
			blocks_total = None
			blocks_used  = None
			rr_4k_min = None
			rr_4k_avg = None
			rr_4k_max = None
			rr_4k_sd  = None
			rw_4k_min = None
			rw_4k_avg = None
			rw_4k_max = None
			rw_4k_sd  = None
			seqw_100m = None

			for fo_r in [fo_r0, fo_r1]:
				for line in fo_r.readlines():
					#Cons.P("%d [%s]" % (i, line.strip()))
					if i == 0:
						dt = line.strip()
					# 4k rand read
					elif i == 1:
						t = line.split()
						if len(t) != 8:
							raise RuntimeError("Unexpected format [%s]" % line)
						# All in us
						rr_4k_min = int(t[4])
						rr_4k_avg = int(t[5])
						rr_4k_max = int(t[6])
						rr_4k_sd  = int(t[7])
					elif i == 2:
						t = line.split()
						if len(t) != 8:
							raise RuntimeError("Unexpected format [%s]" % line)
						# All in us
						rw_4k_min = int(t[4])
						rw_4k_avg = int(t[5])
						rw_4k_max = int(t[6])
						rw_4k_sd  = int(t[7])
					elif i == 3:
						t = line.split()
						if len(t) != 8:
							raise RuntimeError("Unexpected format [%s]" % line)
						# All of the min, avg, max are the same since there is only 1 request
						# at a time.
						seqw_100m = int(t[4])
					elif i == 6:
						t = line.split()
						if (len(t) != 6) or (t[0] != "/dev/xvdc"):
							raise RuntimeError("Unexpected format [%s]" % line)
						blocks_total = int(t[1])
						blocks_used  = int(t[2])

					i += 1
					if i == 7:
						block_used_percent = round(100.0 * blocks_used / blocks_total, 1)
						if block_used_percent_prev != block_used_percent:
							fo_w.write((fmt + "\n") % (dt
								, (100.0 * blocks_used / blocks_total)
								, rr_4k_min, rr_4k_avg, rr_4k_max, rr_4k_sd
								, rw_4k_min, rw_4k_avg, rw_4k_max, rw_4k_sd
								, seqw_100m
								))
						block_used_percent_prev = block_used_percent
						i = 0
						dt = None
						blocks_total = None
						blocks_used  = None
						rr_4k_min = None
						rr_4k_avg = None
						rr_4k_max = None
						rr_4k_sd  = None
						rw_4k_min = None
						rw_4k_avg = None
						rw_4k_max = None
						rw_4k_sd  = None
						seqw_100m = None
		Cons.P("Created %s %d" % (fn_plot_data, os.path.getsize(fn_plot_data)))
