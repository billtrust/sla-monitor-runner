import os
import sys
import json
import boto3
import signal
import subprocess
from time import sleep
from datetime import datetime

class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(DatetimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)


def get_timestamp():
    return datetime.today().timestamp()


def split_groups(groups):
    try:
        groups = groups.split(",")
    except AttributeError:
        groups = []

    return groups


def exec_command(command):
    """Shell execute a command and return the exit code."""
    try:
        startTime = get_timestamp()
        p = subprocess.run(command,  stdout=subprocess.PIPE,  stderr=subprocess.STDOUT, shell=True)
        length = round(get_timestamp() - startTime, 4)
    except Exception as e:
        print("Error executing command: {}".format(e))
        return 1, None
    return p, length


def get_args():
    args = {
        "sns_topic_name": os.getenv("SLARUNNER_SNSTOPICNAME") or None,
        "s3_bucket_name": os.getenv("SLARUNNER_S3BUCKETNAME") or None,
        "command": os.getenv("SLARUNNER_COMMAND") or None,
        "service": os.getenv("SLARUNNER_SERVICE") or None,
        "groups": os.getenv("SLARUNNER_GROUPS") or None,
        "delay": os.getenv("SLARUNNER_DELAY") or None,
        "dry_run": bool(os.getenv("SLARUNNER_DRYRUN"))
    }
    if args["command"] == None or args["delay"] == None or args["service"] == None or args["sns_topic_name"] == None:
        print("Missing required arguments:")
        if not args["delay"]:
            print("    Delay ($SLARUNNER_DELAY) is a required argument.")
        if not args["command"]:
            print("    Command ($SLARUNNER_COMMAND) is a required argument.")
        if not args["service"]:
            print("    Service ($SLARUNNER_SERVICE) is a required argument.")
        if not args["sns_topic_name"]:
            print("    SNS Topic Name ($SLARUNNER_SNSTOPICNAME) is a required argument.")
        sys.exit(1)
    return args

def get_topic_arn(sns_topic):
    region = boto3.session.Session().region_name
    account_id = boto3.client('sts').get_caller_identity()["Account"]
    return "arn:aws:sns:%s:%s:%s" % (region, account_id, sns_topic)


def run_loop(args):
    print("Beginning new loop...")
    exit_info, length = exec_command(args["command"].split(" "))
    result = exit_info.returncode == 0
    now = int(get_timestamp())
    message = {
            "timestamp": now,
            "succeeded": result,
            "service": args["service"],
            "testExecutionSecs": length,
            "groups": split_groups(args["groups"])
        }
    message_encoded = json.dumps(message, cls=DatetimeEncoder, separators=(",", ":"))
    arn = get_topic_arn(args["sns_topic_name"])
    if result:
        result_name="SUCCESS"
    else:
        result_name="FAILURE"
    print("Test result: {} with exit code {}; Execution time: {}".format(result_name, exit_info.returncode, length))
    filename="%s/%s_%s" % (args["service"], now, result_name)
    
    if not args["dry_run"]:
        client = boto3.client('sns')
        response = client.publish(
            TopicArn=arn,
            MessageStructure='json',
            Message=json.dumps({'default': message_encoded})
        )
        if args["s3_bucket_name"]:
            s3 = boto3.client("s3")
            s3.put_object(Body=exit_info.stdout, Bucket=args["s3_bucket_name"], Key=filename)

        sleep(int(args["delay"]))
    else:
        print(arn)
        print(message_encoded)
        print(exit_info.stdout.decode('utf8'))
        print(filename)


def main():
    here = os.path.abspath(os.path.dirname(__file__))
    about = {}
    with open(os.path.join(here, 'version.py'), 'r') as f:
        exec(f.read(), about)

    print('SLA Runner version {}'.format(about['__version__']))

    args = get_args()
    print("COMMAND:   " + args["command"])
    print("SNS TOPIC: " + args["sns_topic_name"])
    print("S3 BUCKET: " + args["s3_bucket_name"])
    try:
        while True:
            run_loop(args)
    except KeyboardInterrupt:
        print("Exiting")
        sys.exit(1)