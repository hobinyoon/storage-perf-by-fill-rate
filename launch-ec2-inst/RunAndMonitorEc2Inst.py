import boto3
# Boto: http://boto3.readthedocs.org/en/latest/
import pprint
import sys
import time

sys.path.insert(0, "../util/python")
import Cons
import Util

_boto_client = None

def Run():
	with Cons.MeasureTime("Running an EC2 instance ..."):
		global _boto_client
		if _boto_client == None:
			_boto_client = boto3.client("ec2")

		inst_id = _RunEc2Inst()
		_KeepCheckingInst(inst_id)


def _RunEc2Inst():
	response = _boto_client.run_instances(
			#DryRun = True
			DryRun = False
			, ImageId = "ami-1fc7d575"
			, MinCount=1
			, MaxCount=1
			, SecurityGroups=["cass-server"]
			, EbsOptimized=True
			, InstanceType="r3.xlarge"
			, BlockDeviceMappings=[
				{
					'DeviceName': '/dev/sdc',
					'Ebs': {
						'VolumeSize': 16384,
						'DeleteOnTermination': True,
						'VolumeType': 'gp2',
						'Encrypted': False
						},
					},
				],
			)
			# What's the defalt value, when not specified? Might be True. I see the
			# Basic CloudWatch monitoring on the web console.
			# Monitoring={
			#     'Enabled': True|False
			# },
			#
			# "stop" when not specified.
			#   InstanceInitiatedShutdownBehavior='stop'|'terminate',
	Cons.P("Response:")
	Cons.P(Util.Indent(pprint.pformat(response, indent=2, width=100), 2))
	if len(response["Instances"]) != 1:
		raise RuntimeError("len(response[\"Instances\"])=%d" % len(response["Instances"]))
	inst_id = response["Instances"][0]["InstanceId"]
	return inst_id


def _KeepCheckingInst(inst_id):
	prev_state = None
	just_printed_dot = False

	while True:
		response = None
		state = None
		try:
			response = _boto_client.describe_instances(InstanceIds=[inst_id])
			# Note: describe_instances() returns StateReason, while
			# describe_instance_status() doesn't.

			#Cons.P(pprint.pformat(response, indent=2, width=100))
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == "InvalidInstanceID.NotFound":
				state = "NotFound"
			else:
				raise

		if state == None:
			state = response["Reservations"][0]["Instances"][0]["State"]["Name"]

		if state == prev_state:
			if just_printed_dot:
				sys.stdout.write(".")
			else:
				sys.stdout.write(" .")
			sys.stdout.flush()
			just_printed_dot = True
			time.sleep(1)
		else:
			if prev_state == None:
				sys.stdout.write("  State: ")
			else:
				sys.stdout.write(" ")
			sys.stdout.write(state)
			sys.stdout.flush()
			just_printed_dot = False
			prev_state = state

			if state == "terminated" \
					or state == "running":
				break

			if state == "shutting-down":
				state_reason = response["Reservations"][0]["Instances"][0]["StateReason"]["Message"]
				sys.stdout.write(" (%s)" % state_reason)
				sys.stdout.flush()

			time.sleep(1)
	print ""
