## FedRAMP Govcloud Egress Proxy
Fork of https://github.com/aws-samples/outbound-vpc-filtering-proxy for use with Trellix Endpoint FedRAMP MGMT.

Documents on Confluence https://confluence-lvs.prod.mcafee.com/display/CCS/Egress+Proxy.

## Deploy Process
1. Create base AMI using EC2 Image Builder
    - Template: source/ec2-image-builder-cf.yaml
    - Deploy w/ script:
    ```
    ./deploy-image.sh -n <cloudformation stack name> -r <iam role name> -c "Version=<version>" #default Version=1.0.0 
    ```
    - Run pipeline:
    ```
    aws imagebuilder start-image-pipeline-execution --image-pipeline-arn <pipeline arn>
    ```
2. Deploy Squid stack
    - Template: source/outbound-proxy-cf.yaml
    - Deploy w/ script:
    ```
    ./deploy-squid.sh -n <cloudformation stack name> -r <iam role name> -c "LatestAmiId=<image> VpcId=<vpc> \ 
        PrivateSubnetIDs=<private subenets> PublicSubnetIDs=<public subetnets>"
    ```

## Client Configuration
- Linux - set via environment variables
```
#for clients needing lowercase
export http_proxy=http://<proxy-nlb>:<proxy-port>
export https_proxy=http://<proxy-nlb>:<proxy-port>
export no_proxy=localhost,127.0.0.1,<ec2-instance-metadata-service(169.254.169.254)>,<vpc-private-ip>,<vpc-endpoint-fqdn>,<k8s-service>,<eks-cluster>,<fed-private-domain>

#for clients needing UPPERCASE
export HTTP_PROXY=$http_proxy
export HTTPS_PROXY=$https_proxy
export NO_PROXY=$no_proxy
```

