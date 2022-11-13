import torch
import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
from urllib.request import urlopen
from PIL import Image
import numpy as np
import json
import sys
import time
import boto3
import base64
import os

model = models.resnet18(pretrained=True)
model.eval()

sqs = boto3.client('sqs')
s3 = boto3.client('s3')
request_queue_url = 'https://sqs.us-east-1.amazonaws.com/477824770261/RequestQueue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/477824770261/ResponseQueue'
input_bucket_name = 'cc-project-input'
output_bucket_name = 'cc-project-output'

def upload_file(file_name, bucket, output_flag):
    object_name = os.path.basename(file_name)
    if output_flag:
        object_name = object_name.split('.')[0]
    s3.upload_file(file_name, bucket, object_name)
 
    return True

while True:
    try:
        msg = sqs.receive_message(QueueUrl=request_queue_url,AttributeNames=['All'], MessageAttributeNames =['All'])
        bytes = str.encode(msg['Messages'][0]['Body'])

        img_name = msg['Messages'][0]['MessageAttributes']['ImageName']['StringValue']  #need to update as per changes in web tier
        img_add = f'/home/ubuntu/{img_name}'

        file = open(img_add, 'wb')
        img_bytes = base64.b64decode((bytes))
        file.write(img_bytes)
        file.close()
        img = Image.open(img_add)

        img_tensor = transforms.ToTensor()(img).unsqueeze_(0)
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs.data, 1)

        with open('/home/ubuntu/classifier/imagenet-labels.json') as f:
            labels = json.load(f)
        result = labels[np.array(predicted)[0]]

        save_name = f"{img_name},{result}"
        #print(f"-----------------------------------> {save_name}")
        with open(img_add+'-output.txt', 'w') as f:
            f.write(save_name)

        msg_response = None

        #msg_response  = sqs.send_message(QueueUrl=response_queue_url, MessageBody=save_name)
        msg_response  = sqs.send_message(QueueUrl=response_queue_url, MessageAttributes={'ImageName': {
            'DataType': 'String',
            'StringValue': img_name
        }}, MessageBody=save_name)

        upload_file(img_add, input_bucket_name, False)
        upload_file(img_add+'-output.txt', output_bucket_name, True)

        del_responce = None

        del_responce = sqs.delete_message(QueueUrl=request_queue_url , ReceiptHandle=msg['Messages'][0]['ReceiptHandle'])

        print(f"{save_name}")
        #print('Sleep for 10 sec...')
        #time.sleep(10)
    except:
        print('Sleep for 5 sec...')
        time.sleep(5)

