import boto3
import os
from datetime import datetime, timezone

def lambda_handler(event, context):
    # Get the tag filter from the environment variables
    tag_key = os.getenv('INSTANCE_TAG_KEY')
    tag_value = os.getenv('INSTANCE_TAG_VALUE')
    
    if not tag_key or not tag_value:
        raise ValueError("Environment variables INSTANCE_TAG_KEY and INSTANCE_TAG_VALUE must be set.")
    
    # Create an EC2 client using the default AWS credentials provided by the Lambda execution environment
    ec2_client = boto3.client('ec2')
    
    # Get a list of all EC2 instances
    instances = ec2_client.describe_instances()['Reservations']
    
    # Find volumes attached to instances with the specified tags
    volumes_to_snapshot = []
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
            if instance_tags.get(tag_key) == tag_value:
                for block_device in instance.get('BlockDeviceMappings', []):
                    if 'Ebs' in block_device:
                        volumes_to_snapshot.append({
                            'VolumeId': block_device['Ebs']['VolumeId'],
                            'InstanceId': instance['InstanceId'],
                            'InstanceTags': instance_tags
                        })

    # Create snapshots for the identified volumes
    for volume in volumes_to_snapshot:
        volume_id = volume['VolumeId']
        instance_id = volume['InstanceId']
        instance_tags = volume['InstanceTags']
        
        description = f"Snapshot of volume {volume_id} from instance {instance_id} with tag {tag_key}: {tag_value}"
        
        print(f"Creating snapshot for volume {volume_id} from instance {instance_id}.")
        
        # Create the snapshot
        snapshot = ec2_client.create_snapshot(
            VolumeId=volume_id,
            Description=description
        )
        
        snapshot_id = snapshot['SnapshotId']
        
        # Add tags to the snapshot
        snapshot_tags = [
            {'Key': 'Name', 'Value': f"Snapshot of {volume_id}"},
            {'Key': tag_key, 'Value': tag_value}
        ]
        
        # Add original instance tags to snapshot
        for key, value in instance_tags.items():
            snapshot_tags.append({'Key': key, 'Value': value})
        
        ec2_client.create_tags(
            Resources=[snapshot_id],
            Tags=snapshot_tags
        )
        
        print(f"Snapshot {snapshot_id} created for volume {volume_id} from instance {instance_id}.")

    return {
        'statusCode': 200,
        'body': 'Snapshots created successfully.'
    }
