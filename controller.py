import boto3
import time

sqs = boto3.client('sqs')
ec2 = boto3.client('ec2')

ami_id = 'ami-0bb1040fdb5a076bc'
min_count = int(0)
max_count = int(19)
current_count = 0
instance_type = 't2.micro'
key_name = 'KP1'
security_group_id = 'sg-0febb3a5f36bbd06d'
iam_instance_profile = 'arn:aws:iam::477824770261:instance-profile/EC2-SQS-S3-FullAccess'
instance_name = 'app_instance'
userdata = '#cloud-boothook \n#!/bin/bash \nsudo apt update \nsudo apt install -y python3 \nsudo apt install -y python3-flask \nsudo apt install -y python3-boto3 \nsudo apt install -y tmux \nsudo apt install -y awscli \nmkdir /home/ubuntu/.aws \naws s3 cp s3://cc-project-extra/config /home/ubuntu/.aws/ \naws s3 cp s3://cc-project-extra/config ~/.aws/ \naws s3 cp s3://cc-project-extra/app.py /home/ubuntu/ \nchmod +777 /home/ubuntu/app.py \ntouch /home/ubuntu/log.txt \nchmod -R 777 /home/ubuntu \nsudo -u ubuntu python3 /home/ubuntu/app.py \n'
instance_list = []
scale_in_count=0

instances = ec2.describe_instances( Filters = [{ 'Name': 'instance-state-code', 'Values': [ '0', '16' ] }, { 'Name': 'image-id', 'Values': [ami_id] }] )

print(instances)

current_count = int(len(instances['Reservations']))
print('Current Count: ' , current_count)

#Populating Instance Ids for App Tier Servers already running
for x in instances['Reservations']:
    instance_list.append(x['Instances'][0]['InstanceId'])

print('Instance List: \n', instance_list)

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/477824770261/RequestQueue'

while True:
    try:
        print('Polling the Request Queue...')
        queue_attr = sqs.get_queue_attributes(QueueUrl = request_queue_url, AttributeNames = ['All'])
        num_visible_msg = int(queue_attr['Attributes']['ApproximateNumberOfMessages'])
        num_invisible_msg = int(queue_attr['Attributes']['ApproximateNumberOfMessagesNotVisible'])
        total_msg = int(num_visible_msg + num_invisible_msg)
        
        print('Total Messages in Queue: ', total_msg)
        print('Total EC2 Instance Running: ', current_count)
        
        #Scale Out App Tier Instances
        if total_msg > current_count and current_count < max_count:
            print('Scaling Out...')
            #instances = ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1, InstanceType=instance_type, KeyName=key_name, SecurityGroupIds=[security_group_id,], IamInstanceProfile={'Arn' : iam_instance_profile}, TagSpecifications=[{'ResourceType': 'instance', 'Tags' : [{'Key': 'Name', 'Value': 'app-instance'+str(current_count)},]},], UserData=userdata)
            #instance_list.append(instances['Instances'][0]['InstanceId'])
            #current_count += 1
            for i in range(current_count, min(total_msg-current_count,max_count)):
                instances = ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1, InstanceType=instance_type, KeyName=key_name, SecurityGroupIds=[security_group_id,], IamInstanceProfile={'Arn' : iam_instance_profile}, TagSpecifications=[{'ResourceType': 'instance', 'Tags' : [{'Key': 'Name', 'Value': 'app-instance'+str(i)},]},], UserData=userdata)
                instance_list.append(instances['Instances'][0]['InstanceId'])
                print(current_count)
                current_count += 1
            
        #Scale In App Tier Instances
        elif total_msg <= (current_count-1) and current_count > min_count:
            if scale_in_count > 3:
                print('Scaling In...')
                for i in range(current_count,total_msg,-1):
                    ec2.terminate_instances(InstanceIds = [instance_list.pop()])
                    current_count -= 1
                    scale_in_count = 0
                    print(current_count)
            else:
                scale_in_count += 1
        elif current_count<min_count:
            print('Starting minimum number of instances...')
            instances = ec2.run_instances(ImageId=ami_id, MinCount=1, MaxCount=1, InstanceType=instance_type, KeyName=key_name, SecurityGroupIds=[security_group_id,], IamInstanceProfile={'Arn' : iam_instance_profile}, TagSpecifications=[{'ResourceType': 'instance', 'Tags' : [{'Key': 'Name', 'Value': 'app-instance'+str(current_count)},]},], UserData=userdata)
            instance_list.append(instances['Instances'][0]['InstanceId'])
            current_count += 1
            
        else:
            print('No Scaling Needed...')
        time.sleep(5)
    except Exception as e:
        print(e)
        break
    

