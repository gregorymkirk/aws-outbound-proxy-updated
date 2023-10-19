def lambda_handler(event, context):
    import json
    import boto3
    import os
    import datetime
    import base64
    import gzip

    cw_data = event['awslogs']['data']
    print(f'data: {cw_data}')
    compressed_payload = base64.b64decode(cw_data)
    uncompressed_payload = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed_payload)
    print(f'payload: {payload}' )
    message = payload['logEvents'][0]['message']
    print(f'Messsage: {message}')

    #split the message on the first ":", then strip spaces to get the arn from the message.
    arn=(message.split(':',1)[1]).strip()
    print(arn)

    # Get the updated AMI build by our pipeline.
    imagebuilder = boto3.client('imagebuilder')
    image = imagebuilder.get_image(imageBuildVersionArn=arn)
    ami=image["image"]["outputResources"]["amis"][0]["image"]
    print(ami)

    #Get our current launch template  information, we will use this to build a new launch Template Version updated to use our new AMI.
    asgname=os.environ['AUTOSCALING_GROUP']
    autoscaling = boto3.client('autoscaling')
    asg=autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asgname])
    
    if asg['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'statusCode': asg['ResponseMetadata']['HTTPStatusCode'],
            'body': 'failed to retrieve existing launch configuration'
        }
    ltid=asg['AutoScalingGroups'][0]['LaunchTemplate']['LaunchTemplateId']
    ltver=asg['AutoScalingGroups'][0]['LaunchTemplate']['Version']
    print("Launch Template: ",ltid, " - ", ltver)

    #Create tne new Launch Template Version.
    dt=datetime.datetime.now()
    datestamp = dt.strftime('%Y%m%d-%H%M')
    description='squid-proxy-' + datestamp

    ec2=boto3.client("ec2")
    response = ec2.create_launch_template_version(
        LaunchTemplateId=ltid,
        SourceVersion=ltver,
        VersionDescription=description,
        LaunchTemplateData={
            'ImageId':ami
        }
    )
    newver=response['LaunchTemplateVersion']['VersionNumber']

    #Check that we got a 200 response (created a new launch template version) here.
    print("Create new version Response: ", response['ResponseMetadata']['HTTPStatusCode'])
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
        'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
        'body': 'failed to create launch configuration'
        }

    response=autoscaling.start_instance_refresh(
        AutoScalingGroupName=asgname,
        Strategy='Rolling',
        DesiredConfiguration={
            'LaunchTemplate':{
                'LaunchTemplateId': ltid,
                'Version': str(newver)
            }
        },
        Preferences={
            'MinHealthyPercentage': 100,
            'CheckpointDelay': 120,
            'ScaleInProtectedInstances': 'Refresh',
            'StandbyInstances': 'Terminate'
        }
    )    
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        return {
            'statusCode': response['ResponseMetadata']['HTTPStatusCode'],
            'body': 'failed to to initiate instance refresh'
        }
    else:
        return {
            'statusCode': 200,
            'body': "Instance Refresh ID: " + response['InstanceRefreshId']
        }
