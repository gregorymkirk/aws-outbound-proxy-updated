#!/bin/bash
# Deploy squid cloudformation stack
# © Copyright 2021 McAfee, Corp.

set -e

## The deployment is driven by the following options:
usage() {
    echo "Usage: "
    echo "deploy-squid.sh -n <stack name> -r <role> -c <cloudformation params>"
    echo "Where "
    echo "-n <stack name>: cloudformation stack name"
    echo "-r <role>: iam role name for cloudformation to run as"
    echo "-c <cloudformation params>: cloudformation parameters"
    echo "-h: Print this help"
}

#parse options
while getopts "n:r:c:h" opt; do
  case $opt in
    n)
        stackName=${OPTARG}
        ;;
    r)
        iamRoleName=${OPTARG}
        ;;
    c)
        cfnParams=${OPTARG}
        ;;
    h)
        usage
        exit 0
        ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

#arguments required
if [ -z "${stackName}" ] || [ -z "${iamRoleName}" ] || [ -z "${cfnParams}" ];
  then
    echo "Arguments required"
    usage
    exit 1
fi

#read allowed domains from disk and append to cloudformation parameters
echo "Getting allowed domains..."
allowedDomains=$(cat ../source/allowed.domains.txt | tr -d " " | tr "\n" ",")
cfnParams+=" AllowDomains=${allowedDomains}"
echo "allowed domains: "$allowedDomains

#pre-req, create/verify cloudformation role and permissions
policyArns=("arn:aws:iam::aws:policy/IAMFullAccess" "arn:aws:iam::aws:policy/AmazonEC2FullAccess" "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess" "arn:aws:iam::aws:policy/SecretsManagerReadWrite")

if roleArn=$(aws iam get-role --role-name $iamRoleName --output text --query 'Role.[Arn]'); then
    #ensure policies are attached
    for arn in ${policyArns[@]}; do
        aws iam attach-role-policy --role-name $iamRoleName --policy-arn $arn
    done
    echo "Role exists, policies attached"
else
    #create role
    roleArn=$(aws iam create-role --role-name $iamRoleName --assume-role-policy-document file://../source/cfn-role-trust-policy.json --output text --query 'Role.[Arn]')
    #attach policies
    for arn in ${policyArns[@]}; do
        aws iam attach-role-policy --role-name $iamRoleName --policy-arn $arn
    done
    #wait for role propagation
    sleep 60
    echo "Role created and policies attached"
fi

#deploy package
echo "Deploying Cloudformation package..."
if aws cloudformation deploy --template-file ../source/outbound-proxy-cf.yaml \
    --stack-name $stackName --parameter-overrides $cfnParams \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --role-arn $roleArn; then
    echo "CloudFormation successfully deployed the package"
else
    echo "Failed deploying CloudFormation package"
    exit 1
fi 

echo "Done"