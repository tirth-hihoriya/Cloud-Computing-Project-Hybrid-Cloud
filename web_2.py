import boto3
import time
import base64
import os
import random
from flask import Flask, flash, request, g, session
#from flask_session import Session
from flask_caching import Cache
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/home/ubuntu/savedImages'
application = Flask(__name__)
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
sqs=boto3.client('sqs')

#SESSION_TYPE = 'filesystem'
#application.config.from_object(__name__)
#Session(application)

cache_path = '/home/ubuntu/cache/'
cache = Cache(application, config={'CACHE_TYPE': 'FileSystemCache', 'CACHE_DIR': cache_path,})
cache.clear()

request_queue_url = 'https://sqs.us-east-1.amazonaws.com/477824770261/RequestQueue'
response_queue_url = 'https://sqs.us-east-1.amazonaws.com/477824770261/ResponseQueue'

#ctx = application.app_context()
#ctx.push()

@application.route('/')
def hello_world():
        return 'Hello World'

@application.route('/upload', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        file3 = request.files.getlist('myfile')
        for file2 in file3:
            filename = secure_filename(file2.filename)
            path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file2.save(path)
            with open("/home/ubuntu/savedImages/"+filename, "rb") as image2string:
                bytes = base64.b64encode(image2string.read())
                sqs.send_message(QueueUrl=request_queue_url,
                        MessageAttributes={
        'ImageName': {
            'DataType': 'String',
            'StringValue': filename
        }},MessageBody=bytes.decode('ascii'))
                print(filename)
                
        time.sleep(120)
        
        while True:
            try:
                print(filename," -- Checking in Cache.")
                #print("Session keys: ", session.keys())
                #ctx.push()
                #dic = g.dic
                #ctx.pop()
                if cache.get(filename):
                    print(filename," -- Found in cache: ", cache.get(filename))
                    #result = dic[filename][1]
                    result = cache.get(filename)[1]
                    print("File Name: ", filename)
                    print(filename," -- Classification Result: ", result)
                    #sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=cache.get(filename)[0])
                    #print(filename," -- Response Deleted from Queue")
                    #ctx.push()
                    #del g.dic[filename]
                    #ctx.pop()
                    return result
                else:
                    try:
                        print(filename," -- Result not in Cache. Querying SQS...")
                        print(filename," -- Checking for response...")
                        queue_attr = sqs.get_queue_attributes(QueueUrl = response_queue_url, AttributeNames = ['All'])
                        num_visible_msg = int(queue_attr['Attributes']['ApproximateNumberOfMessages'])
                        print('Visible msg: ', num_visible_msg)
                        if num_visible_msg > 0:
                            msg = sqs.receive_message(QueueUrl=response_queue_url, AttributeNames=['All'], MessageAttributeNames=['All'])
                            body = msg['Messages'][0]['Body']
                            resp_filename, result = body.split(',')
                            if filename == resp_filename:
                                print("File Name: ", filename)
                                print(filename," -- Classification Result: ", result)
                                
                                print(filename," -- Deleting from response queue -- ", resp_filename)
                                sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=msg['Messages'][0]['ReceiptHandle'])
                                return result
                            else:
                                print(filename," -- Adding to cache: ", filename, resp_filename)
                                #ctx.push()
                                #g.dic[resp_filename] = list([msg['Messages'][0]['ReceiptHandle'],result])
                                #ctx.pop()
                                #session[resp_filename] = list([msg['Messages'][0]['ReceiptHandle'],result])
                                cache.set(resp_filename, list([msg['Messages'][0]['ReceiptHandle'],result, filename]))
                            
                            print(filename," -- Deleting from response queue -- ", resp_filename)
                            sqs.delete_message(QueueUrl=response_queue_url, ReceiptHandle=msg['Messages'][0]['ReceiptHandle'])
                        else:
                            time.sleep(random.random()*3+1)
                            continue
                            
                    except Exception as e:
                        print(filename," -- Exception Occured...")
                        print(e)
                        
            #except AttributeError as e:
                #ctx.push()
                #g.dic=dict()
                #ctx.pop()
            except Error as e:
                print(filename," -- ",e)
                pass
            
            time.sleep(random.random()*3+1)
        #return 'hi'
        
if __name__ == "__main__":
        application.run(host='0.0.0.0', port='8080')

