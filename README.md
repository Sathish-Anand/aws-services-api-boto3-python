# aws-cost-athena-cloudwatch
This is to get aws cost athena query and cloudwatch metrics and values using boto3 sdk

*Dependency:*

Run the version check to install all the dependencies ``` sh versionCheck.sh```  and hope aws cli is already installed and configured.

***To Run The Project:***
This cost comparison is parallelised between different level using multi processor module.\

``` python3 main.py --months=3```


***Jenkins:***
```awscostandusage.groovy``` is to automate the project to run through jenkins and when the build is failed/successful slack message will be sent to the group. 
