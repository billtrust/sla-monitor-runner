import os
import unittest
import configparser
import boto3
from scripttest import TestFileEnvironment

config = configparser.ConfigParser()
config.read("unittest/test_suite.ini")


def get_environ(section):
    loaded_environ = os.environ.copy()
    for key in config[section]:
        loaded_environ[key.upper()] = config[section][key]
    env = TestFileEnvironment('./test-output', environ=loaded_environ)
    return env


class TestSlaRunner(unittest.TestCase):
    def test_command_is_required(self):
        env = get_environ("test_no_command")
        result = env.run('sla-runner', expect_error=True)
        assert not result.returncode == 0 and 'Command ($SLARUNNER_COMMAND) is a required argument' in result.stdout


    def test_service_is_required(self):
        env = get_environ("test_no_service")
        result = env.run('sla-runner', expect_error=True)
        assert not result.returncode == 0 and 'Service ($SLARUNNER_SERVICE) is a required argument' in result.stdout


    def test_delay_is_required(self):
        env = get_environ("test_no_delay")
        result = env.run('sla-runner', expect_error=True)
        assert not result.returncode == 0 and 'Delay ($SLARUNNER_DELAY) is a required argument' in result.stdout


    def test_sns_topic_is_required(self):
        env = get_environ("test_no_sns")
        result = env.run('sla-runner', expect_error=True)
        assert not result.returncode == 0 and 'SNS Topic Name ($SLARUNNER_SNSTOPICNAME) is a required argument' in result.stdout


    def test_sns_arn_formed_correctly(self):
        env = get_environ("test_full_options")
        region = boto3.session.Session().region_name
        account_id = boto3.client('sts').get_caller_identity()["Account"]
        expected_arn = 'arn:aws:sns:%s:%s:sla-runner-results' % (region, account_id)
        result = env.run('sla-runner')
        assert result.returncode == 0 and expected_arn in result.stdout
    

    def test_invalid_sns_fails(self):
        env = get_environ("test_invalid_sns")
        result = env.run('sla-runner', expect_error=True)
        assert not result.returncode == 0 and 'Topic does not exist' in result.stdout


if __name__ == '__main__':
    unittest.main()
