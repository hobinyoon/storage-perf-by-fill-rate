import errno
import os
import pprint
import re
import subprocess
import sys
import time

import Cons


_ind = 0

class MeasureTime:
	def __init__(self, msg, indent = 0):
		self.msg = msg
		self.indent = indent
		global _ind
		_ind += indent

	def __enter__(self):
		self.start_time = time.time()
		IndPrint(self.msg)
		global _ind
		_ind += 2
		return self

	def __exit__(self, type, value, traceback):
		dur = time.time() - self.start_time
		IndPrint("%.0f ms" % (dur * 1000.0))
		global _ind
		_ind -= 2

	def GetMs(self):
		return (time.time() - self.start_time) * 1000.0


def Indent(s0, ind):
	spaces = ""
	for i in range(ind):
		spaces += " "
	return re.sub(re.compile("^", re.MULTILINE), spaces, s0)


def IndPrint(s0, ind = 0):
	# Thread-safely is not considered
	global _ind
	_ind += ind
	print Indent(s0, _ind)


def BuildHeader(fmt, desc):
	name_end_pos = []
	#print fmt
	# Float, integer, or string
	nep = 0
	for m in re.findall(r"%(([-+]?[0-9]*\.?[0-9]*f)|([-+]?[0-9]*d)|([-+]?[0-9]*s))", fmt):
		#print m[0]
		# Take only the leading number part. Python int() is not as forgiving as C atoi().
		m1 = re.search(r"([1-9][0-9]*)", m[0])
		if nep != 0:
			nep += 1
		nep += int(m1.group(0))
		#print nep
		name_end_pos.append(nep)
	#IndPrint("name_end_pos: %s" % name_end_pos)

	names_flat = "# %s\n" % desc
	names_flat += "#\n"
	names = desc.split()
	#IndPrint("names: %s" % names)

	# Header lines
	lines = []
	for i in range(len(names)):
		fits = False

		for j in range(len(lines)):
			if len(lines[j]) + 1 + len(names[i]) > name_end_pos[i]:
				continue

			while len(lines[j]) + 1 + len(names[i]) < name_end_pos[i]:
				lines[j] += " "
			lines[j] += (" " + names[i])
			fits = True
			break

		if fits:
			continue

		l = "#"
		while len(l) + 1 + len(names[i]) < name_end_pos[i]:
			l += " "
		l += (" " + names[i])
		lines.append(l)

	# Indices for names starting from 1 for easy gnuplot indexing
	ilines = []
	for i in range(len(names)):
		idxstr = str(i + 1)
		fits = False
		for j in range(len(ilines)):
			if len(ilines[j]) + 1 + len(idxstr) > name_end_pos[i]:
				continue

			while len(ilines[j]) + 1 + len(idxstr) < name_end_pos[i]:
				ilines[j] += " "
			ilines[j] += (" " + idxstr)
			fits = True
			break

		if fits:
			continue

		l = "#"
		while len(l) + 1 + len(idxstr) < name_end_pos[i]:
			l += " "
		l += (" " + idxstr)
		ilines.append(l)

	header = ""
	#header = names_flat
	first = True
	for l in lines:
		if first:
			header += l
			first = False
		else:
			header += ("\n" + l)
	for l in ilines:
		header += ("\n" + l)
	return header


# http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def MkDirs(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise


def RunSubp(cmd, env_ = os.environ.copy(), print_cmd = True):
	if print_cmd:
		Cons.P(cmd)
	p = subprocess.Popen(cmd.split(" "), env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	if len(stdouterr) > 0:
		Cons.P(stdouterr)
	return stdouterr
