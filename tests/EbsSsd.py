import datetime
import os
import subprocess
import sys

sys.path.insert(0, "../util/python")
import Cons
import Util

# Test storage performance (local SSD, EBS SSD GP2) by fill rates.
#
# To make an instance store volume with TRIM support available for use on Linux
#   [http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html]
#   - I2, R3's instance store volumes support TRIM
#   - I'm using an i2.xlarge instance.


def Setup():
	with Cons.MeasureTime("Setting up EBS SSD ..."):
		Util.RunSubp("sudo mkdir -p /mnt/ebs-ssd1")
		Util.RunSubp("sudo umount /dev/xvdc || true")

		# EBS volumes come TRIMmed when they are allocated.  Without nodiscard, it
		# takes about 80 secs for a 800GB SSD.
		Util.RunSubp("sudo mkfs.ext4 -m 0 -E nodiscard -L ebs-ssd1 /dev/xvdc")

		# -o discard for TRIM
		Util.RunSubp("sudo mount -t ext4 -o discard /dev/xvdc /mnt/ebs-ssd1")
		Util.RunSubp("sudo chown -R ubuntu /mnt/ebs-ssd1")


_fn_log0 = None
_fn_log1 = None

def Run():
	inst_type = _RunSubp("curl -s http://169.254.169.254/latest/meta-data/instance-type")
	ami_id = _RunSubp("curl -s http://169.254.169.254/latest/meta-data/ami-id")
	public_ip = _RunSubp("curl -s http://169.254.169.254/latest/meta-data/public-ipv4")
	#Cons.P(ec2_inst_type)
	#Cons.P(ami_id)
	#Cons.P(public_ip)

	# Get current datetime, hostname, instance type, ebs type
	global _fn_log0, _fn_log1
	_fn_log0 = "%s-%s-%s-%s" % (
			inst_type
			, datetime.datetime.now().strftime("%y%m%d-%H%M%S")
			, ami_id
			, public_ip)
	_fn_log1 = "../log/ioping/%s" % _fn_log0

	with Cons.MeasureTime("Setting up ..."):
		dn_rand_data = "/mnt/ebs-ssd1/rand-data"
		#Util.RunSubp("rm -rf %s" % dn_rand_data)
		Util.RunSubp("mkdir -p %s" % dn_rand_data)
		Util.RunSubp("dd if=/dev/zero of=%s/zeros bs=1M count=1000 > /dev/null 2>&1" % dn_rand_data)
		Util.RunSubp("mkdir -p /mnt/ebs-ssd1/ioping-tmp")
		#Cons.P("Logging to %s" % _fn_log0)

		Util.RunSubp("mkdir -p ../log/ioping")
		Util.RunSubp("touch %s" % _fn_log1)

	fn_rand_data = None

	while True:
		_MeasurePerf()

		if fn_rand_data == None:
			fn_rand_data = "%s/%s" % (dn_rand_data, datetime.datetime.now().strftime("%y%m%d-%H%M%S"))
		else:
			# Make a new file when the file size becomes too big
			filesize = os.path.getsize(fn_rand_data)
			if filesize > 20 * 1024 * 1024 * 1024:
				fn_rand_data = "%s/%s" % (dn_rand_data, datetime.datetime.now().strftime("%y%m%d-%H%M%S"))

		# /dev/urandom too slow. http://serverfault.com/questions/6440/is-there-an-alternative-to-dev-urandom
		#   dd if=/dev/urandom of=$dn_rand_data/`date +"%y%m%d-%H%M%S.%N"` bs=1M count=20 > /dev/null 2>&1
		#
		# When the device gets full, it raises an exception and terminates.
		# It took 4 days and 12 hours to fill the 16TB EBS SSD volume.
		#   start: 160422-220627
		#   end  : 160427-093745
		cmd = "(openssl enc -aes-256-ctr" \
				" -pass pass:\"$(dd if=/dev/urandom bs=128 count=1 2>/dev/null | base64)\" -nosalt" \
				" < %s/zeros >> %s)" \
				" && sync" \
				% (dn_rand_data, fn_rand_data)
		_RunSubp(cmd)
		sys.stdout.write(".")
		sys.stdout.flush()


def _MeasurePerf():
	# -p period  : Print raw statistics for every period requests.
	# -c count   : Stop after count requests.
	# -i interval: Set time between requests to interval (1s).
	# -q         : Suppress periodical human-readable output.
	#ioping -p 100 -c 200 -i 0 -q
	#
	# Meaningless, since data won't be stored here. Plus, the 8GB EBS SSD is rate
	# limited, slowing down the experiment.
	# ioping -D -p 100 -c 100 -i 0              -q /home/ubuntu/ioping-tmp >> $_fn_log1
	# ioping -D -p 100 -c 100 -i 0 -WWW         -q /home/ubuntu/ioping-tmp >> $_fn_log1
	# ioping -D -p   1 -c   1 -i 0 -WWW -s 100m -q /home/ubuntu/ioping-tmp >> $_fn_log1
	#
	# writes/sec is below 1000. reads/sec is below 100. No need to worry about
	# rate limiting.
	#  $ collectl
	#  $ iostat -xd 1
	#
	# Report free spaces
	# df /dev/xvda1 /dev/xvdc >> $_fn_log1

	cmd = "(date +\"%%y%%m%%d-%%H%%M%%S\" >> %s)" \
			" && (ioping -D -p 100 -c 100 -i 0              -q /mnt/ebs-ssd1/ioping-tmp >> %s)" \
			" && (ioping -D -p 100 -c 100 -i 0 -WWW         -q /mnt/ebs-ssd1/ioping-tmp >> %s)" \
			" && (ioping -D -p   1 -c   1 -i 0 -WWW -s 100m -q /mnt/ebs-ssd1/ioping-tmp >> %s)" \
			" && (df /dev/xvda1 /dev/xvdc >> %s)" \
			% (_fn_log1, _fn_log1, _fn_log1, _fn_log1, _fn_log1)
	_RunSubp(cmd)


def _RunSubp(cmd, env_ = os.environ.copy()):
	p = subprocess.Popen(cmd, shell=True, env=env_, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	# communidate() waits for termination
	stdouterr = p.communicate()[0]
	rc = p.returncode
	if rc != 0:
		raise RuntimeError("Error: cmd=[%s] rc=%d stdouterr=[%s]" % (cmd, rc, stdouterr))
	return stdouterr
