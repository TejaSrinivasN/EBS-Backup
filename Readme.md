# Create a AWS EBS snapshot, Delete the snapshot as if its older than 7 days
For example, we have set the time to be 5 minutes.

## Step-1: Lambda to create EBS
- lambda to create a EBS snapshot of an EC2 instance with a tag specific tag 
- The lambda:- Runtime: Python 3.12
- we should add the ```iam policy``` to the execution role
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeVolumes",
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:CreateTags",
                "ec2:DescribeSnapshots",
                "ec2:DescribeSnapshotAttribute",
                "ec2:DescribeSnapshotTierStatus",
                "ec2:ListSnapshotsInRecycleBin",
                "ec2:DescribeLockedSnapshots",
                "ec2:CreateSnapshots"
            ],
            "Resource": "*"
        }
    ]
}
```
- [create_ebs_snapshot.py](https://raw.githubusercontent.com/TejaSrinivasN/EBS-Backup/main/create_ebs_snapshot.py)
## Step-2: Lambda to delete EBS
- lambda to delete a EBS snapshot of an EC2 instance with a tag specific tag 
- The lambda:- Runtime: Python 3.12
- ```we should add the iam policy to the execution role```
- [delete_EBS_snapshot.py](https://raw.githubusercontent.com/TejaSrinivasN/EBS-Backup/main/delete_EBS_snapshot.py)
## Step-3: create a trigger with EventBridge
- select scheduled events
- give cron expression
  - example: ```cron(00 13 * * ? *)```
  -  this means it will run everydays 24*7 at 13:00 UTC (18:30 IST)
  -   
