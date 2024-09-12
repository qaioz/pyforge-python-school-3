# Homework 10

# AWS
 
## Part 1. First steps, IAM
 
1. Create AWS account using the following guide:
https://aws.amazon.com/resources/create-account/

2. Log in to the AWS Management console using your root credentials.
 
3. Create an IAM User with the following parameters:
 
* Both programmatic and console access
 
* Administrator access - use a AWS managed policy `AdministratorAccess`
 
4. Set up MFA for the newly created user(Optional)
 
5. Log in to the AWS Management console using the newly created user
 
* Note: you can get a link to login to the account from the page of IAM web console right after you created an user.
 
6. Install AWS CLI on your workstation. AWS docs:
https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
 
7. Configure AWS CLI using the credentials for the newly created user.
	Use `aws configure` for that. Instruction:
https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html
	Use us-east AWS region (eg. us-east-1)
	As a result you should have credential file like:
    `cat ~/.aws/credentials`
    `[default]`
    `aws_access_key_id = AKIA...`
    `aws_secret_access_key = *secret_key*`
Test access to your AWS account via AWS CLI by running basic list request:
`aws iam list-users`
 
8. Create IAM Role _Custom_EC2_Role_. Do not create policy for that role.
 
9. Create IAM Policy _Custom_EC2_Policy_ that allows to access all EC2 instances metadata info. Attach this police to the IAM Role _Custom_EC2_Role_ you created.
 
## Part 2. VPC and networking
 
1. Create a new VPC in the account. Name as you wish(eg. hw-vpc). Parameters:
 
* VPC CIDR - chose a CIDR with `/16` size from `10.0.0.0/8`
 
* Subnets: create 1 public subnet `/24` size
 
* Create only Internet gateway (do not create NAT gateway - it's not covered by free tier!)
 
## Part 3. EC2
 
The idea is to get information about the instance that you created. Explained in docs: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
 
Particularly you should get:
 
* Instance ID of the instance
 
* All tags assigned to the instance running the application
 
* Any other metadata you like.
 
What you should do (in general terms):
 
1. Use the VPC from Part 2.
 
2. Create a new Security group _SG-allow-SSH-HTTP_ with a rule that allows SSH and HTTP access from anywhere.
 
3. Create a new key pair _ec2-ssh-key_. Save it to your local PC.
 
4. Create a new EC2 instance with Ubuntu 20.04.  
 
* Search for AMIs. Choose Ubuntu 20.04 ami.
 
* Choose _t2.micro_ instance type(that covered by free tier)
 
* Use a public subnet and enable public IP auto-assignment.
 
* Use instance's user-data script to install aws-cli on a system.
 
* Set following tags:  
	env: dev
	owner: *your_email* 
	project: hw-infra
 
6. Assign IAM Role _Custom_EC2_Role_ you created in Part 1 to the instance.
 
7. SSH to the instance (Use right click on the instance -> _Connect_ to have all instructions)
 
8. Check that the instance can see metadata:
 
* Use AWS CLI to check instance ID and tags of the instance and any metadata entry you like.
 
* Send a screenshot with a results.
For help see docs with available ec2 commands:https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ec2/index.html

10. Stop your instance. (Remember, you most likely want to save free tier hours for your future tests).
 
 
## Part 4. S3
 
1. Create an S3 Bucket _hw-bucket-"any_unique_part"_
2. Upload Sample Files:
* Upload sample file(s) to the bucket. Object(s) could be any type: document, image, or text file.
3. Implement Access Controls:
* Modify(add another Statement) your IAM policy _Custom_EC2_Policy_ to allow Read-Only access only to S3 bucket you just created.
4. Test access to the bucket using the AWS CLI installed on your EC2 instance(start it again if you stopped the instance after Part 3) by running basic list request:
`aws s3 ls`
* Download object(s) from that s3 bucket to your instance.
* Send a screenshot with a output of list and downloaded file.
For help see docs with available s3 commands: https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3/index.html#available-commands
 
And finally, copy your IAM Policy _Custom_EC2_Policy_ json content and attach it .

PS. Do not forget to Stop your instance after all hw activity.
That it. Well done!