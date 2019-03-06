data "aws_caller_identity" "current" {}

resource "aws_iam_role" "sla-monitor-runner-role" {
  name = "sla-monitor-runner-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": [
            "ec2.amazonaws.com",
            "ecs-tasks.amazonaws.com"
            ],
        "AWS": [
            "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "sla-monitor-runner-policy" {
  name = "sla-monitor-runner-policy"
  path = "/"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SLARunnerSNS",
            "Action": [
                "sns:Publish"
            ],
            "Effect": "Allow",
            "Resource": "${aws_sns_topic.sla-monitor-report-processing.arn}"
        },
        {
            "Sid": "SLARunnerS3",
            "Action": [
                "s3:*"
            ],
            "Effect": "Allow",
            "Resource": [
                "${aws_s3_bucket.sla-monitor-runner-logs-bucket.arn}",
                "${aws_s3_bucket.sla-monitor-runner-logs-bucket.arn}/*"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "sla-monitor-runner-policy-attach" {
  role       = "${aws_iam_role.sla-monitor-runner-role.name}"
  policy_arn = "${aws_iam_policy.sla-monitor-runner-policy.arn}"
}
