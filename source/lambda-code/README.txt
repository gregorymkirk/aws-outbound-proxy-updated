Labda code is kepy in the deploysquid.py file for ease of maintenance and editing.

Currently the Cloudformation template uses INLINE code deployment.  
So the code will need to be copied from deploysquid.py to the approrpiate location in
outbound-proxy-cf.yaml.  Currintely si is around line 1154 in the code, 
in the ProxyUpdaterLmabdaFunction resource block, after the line begining with "ZipFile: >"

 
  ProxyUpdaterLambdaFunction:
    Type: AWS::Lambda::Function
    Properties: 
      Code: 
          ZipFile: >
            def lambda_handler(event, context):

