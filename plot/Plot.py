import os
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util


def LocalSsd():
	# Time, used_1k_blocks, available
	# 4k_rand_read_lat_min, 4k_rand_read_lat_avg, 4k_rand_read_lat_max, 4k_rand_read_lat_sd
	# 4k_rand_write_lat_min, 4k_rand_write_lat_avg, 4k_rand_write_lat_max, 4k_rand_write_lat_sd
	# 100m_seq_write

	fn = "i2.xlarge-160425-011750-ami-1fc7d575-54.146.53.151"
	_GenLocalSsdData(fn)
	_PlotLocalSsdRandR4k(fn)
	_PlotLocalSsdRandR4kLog(fn)
	_PlotLocalSsdRandW4k(fn)
	_PlotLocalSsdRandW4kLog(fn)
	_PlotLocalSsdSeqW100m(fn)


def _GenLocalSsdData(fn):
	fn_plot_data = "plot-data/%s" % fn
	fn_raw = "../tests/ioping-log/%s" % fn

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

			
def _PlotLocalSsdSeqW100m(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/seqw-100m-lat-%s.pdf" % fn

	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out

		Util.RunSubp("gnuplot %s/seqw-100m.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotLocalSsdRandR4k(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randr-4k-lat-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randr-4k.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotLocalSsdRandR4kLog(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randr-4k-lat-log-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randr-4k-log.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotLocalSsdRandW4k(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randw-4k-lat-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randw-4k.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))


def _PlotLocalSsdRandW4kLog(fn):
	fn_in = "plot-data/%s" % fn
	fn_out = "plot-data/randw-4k-lat-log-%s.pdf" % fn
	with Cons.MeasureTime("Plotting %s" % fn_out):
		env = os.environ.copy()
		env["FN_IN"] = fn_in
		env["FN_OUT"] = fn_out
		Util.RunSubp("gnuplot %s/randw-4k-log.gnuplot" % os.path.dirname(__file__), env)
		Cons.P("Created %s %d" % (fn_out, os.path.getsize(fn_out)))




#def _RunSubp(cmd, env_, print_cmd=False):
#	if print_cmd:
#		Cons.P(cmd)
#	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#	# communidate() waits for termination
#	stdouterr = p.communicate()[0]
#	rc = p.returncode
#	if rc != 0:
#		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
#	if len(stdouterr) > 0:
#		Cons.P(stdouterr)
#
#
#def _TicsInterval(v_max):
#	# Get most-significant digit
#	# 1 -> 0.5 : 2 tic marks
#	# 2 -> 1   : 2 tic marks
#	# 3 -> 1   : 3 tic marks
#	# 4 -> 2   : 2 tic marks
#	# 5 -> 2   : 2 tic marks
#	# 6 -> 2   : 3 tic marks
#	# 7 -> 2   : 3 tic marks
#	# 8 -> 2   : 4 tic marks
#	# 9 -> 2   : 4 tic marks
#	a = [0.5, 1, 1, 2, 2, 2, 2, 4, 2]
#
#	v_max = float(v_max)
#	v = v_max
#	if v >= 1.0:
#		v_prev = v
#		while v >= 1.0:
#			v_prev = v
#			v /= 10.0
#		msd = int(v_prev)
#	else:
#		while v < 1.0:
#			v *= 10.0
#		msd = int(v)
#
#	base = math.pow(10, math.floor(math.log10(v_max)))
#	ti = a[msd - 1] * base
#	return ti
