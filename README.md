# Cloud-Computing-Project-Hybrid-Cloud
## CSE 546: Cloud Computing Project-3


Group members:
 - Deval Pandya - 1225424200
 - Karthik Ravi Kumar - 1225910467
 - Tirth Hihoriya - 1225413475 
 

<hr>

SQS queue names: `RequestQueue` and `ResponseQueue`

S3 bucket names: `cc-project-input` and `cc-project-output`

<hr>

## Problem Statement
To build a scalable cloud web app in a hybrid cloud environment using AWS resources and OpenStack that recognizes images based on a given classifying model. The processing cloud instances scale up and down based on the inflow of requests. The app uses  AWS EC2, AWS SQS, and AWS S3 services, DevStack utilities and OpenStack. The problem that we are solving is that the auto-scaling implemented can process higher loads of requests by optimizing the number of instances according to the need. This problem is important for us to solve as it helps us in understanding the key concepts of hybrid cloud computing and setting up our own private cloud.


## Member Tasks
### Deval Pandya - (ASU ID: 1225424200)
I have designed the end to end flow for this project like determining the OpenStack and AWS components to be used and setting them up like SQS Queues, S3 Buckets, AWS and OpenStack Security Groups, EC2 and OpenStack instances, their user data, their volume configurations, IAM instance profiles. I also played a part in designing the logic for Web Tier, App Tier, and Controller. I implemented the code for the controller which is used for Autoscaling of App Tier instances as per the number of messages in the Request Queue. I did the testing for the whole application which involved sending several requests (Single/Concurrent) from the workload generators provided to us and optimized the algorithms of App Tier and Web Tier in order to showcase the features of autoscaling in our project.



### Karthik – (ASU ID: 1225910467).
I have designed the Web tier. The listener part of the web tier includes receiving messages from the user, storing it and encoding the images. Other parts include setting up and sending messages to the request queue,testing the request queue, receiving messages from the response queue and printing the output. I also designed the cache for reducing the response retrieval time using the flask caching library. If the required response for the input is not present in the cache, the SQS will be queried for the result. I have tested the working of the cache system and the SQS queue for this functionality.



### Tirth Hihoriya  -  (ASU ID: 1225413475 )
I worked on the project's openstack component. First, I installed OpenStack. Initially, I had several difficulties in the setup due to numerous compatibility issues that arose when completing the installation procedures. Then I sorted out all the requirements, and it finally worked. After that, I concentrated on network setup and security groups.  I also created the App-Tier. Basic image classification software is included in the app-tier. It receives and handles a job from RequestQueue. When it is finished, it sends the output to the Response Queue. It also keeps the input in an input bucket and the output in an output bucket. If no fresh tasks are assigned to it, it waits 5 seconds. I thoroughly evaluated the app-tier code and changed it to make it more robust.
 
 <hr>
 
### Video for full working project

Login with your ASU id to see it.
