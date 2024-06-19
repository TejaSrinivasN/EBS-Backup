import boto3
import os
from datetime import datetime, timezone, timedelta

def lambda_handler(event, context):
    # Get the value of 'x' seconds from the environment variable
    try:
        x_seconds = int(os.getenv('SNAPSHOT_AGE_SECONDS'))
    except (TypeError, ValueError):
        raise ValueError("Environment variable SNAPSHOT_AGE_SECONDS is not set or not an integer.")

    # Get the tag filter values from the environment variables
    tag_key = os.getenv('INSTANCE_TAG_KEY')
    tag_value = os.getenv('INSTANCE_TAG_VALUE')
    
    if not tag_key or not tag_value:
        raise ValueError("Environment variables INSTANCE_TAG_KEY and INSTANCE_TAG_VALUE must be set.")
    
    # Create an EC2 client using the default AWS credentials provided by the Lambda execution environment
    ec2_client = boto3.client('ec2')
    
    # Get the current time in UTC
    current_time = datetime.now(timezone.utc)
    
    # Calculate the time threshold
    time_threshold = current_time - timedelta(seconds=x_seconds)
    
    # Get a list of all EBS snapshots
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])['Snapshots']
    
    # Get a list of all EC2 instances
    instances = ec2_client.describe_instances()['Reservations']
    
    # Create a mapping from volume IDs to instance tags
    volume_tags = {}
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            for block_device in instance.get('BlockDeviceMappings', []):
                if 'Ebs' in block_device:
                    volume_id = block_device['Ebs']['VolumeId']
                    volume_tags[volume_id] = instance_tags
    
    # Loop through the snapshots and delete the ones older than x seconds and matching the instance tags
    for snapshot in snapshots:
        start_time = snapshot['StartTime']
        snapshot_id = snapshot['SnapshotId']
        volume_id = snapshot['VolumeId']
        
        # Check if the snapshot is older than x seconds
        if start_time < time_threshold:
            # Check if the snapshot's volume is associated with an instance having the specified tag
            instance_tags = volume_tags.get(volume_id, {})
            if instance_tags.get(tag_key) == tag_value:
                print(f"Deleting snapshot {snapshot_id} which was created at {start_time} with tag {tag_key}: {tag_value}.")
                # Delete the snapshot
                ec2_client.delete_snapshot(SnapshotId=snapshot_id)
            else:
                print(f"Snapshot {snapshot_id} does not have the tag {tag_key}: {tag_value} in its associated instance. Skipping.")
        else:
            print(f"Snapshot {snapshot_id} created at {start_time} is within the {x_seconds} seconds threshold. Skipping.")

    print("Script execution completed.")
    return {
        'statusCode': 200,
        'body': 'Old snapshots deleted successfully.'
    }
