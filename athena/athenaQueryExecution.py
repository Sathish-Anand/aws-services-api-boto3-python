import boto3
import botocore
import time
import io
import re
import constants.csvFunctions as csv
import athena.athenaCostQueries as acq
import stsAccount.changeSTSaccount as stsa

session = boto3.Session()

def athena_query(client, params, query):
    start_query_response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': params['database']
        },
        ResultConfiguration={
            'OutputLocation': 's3://' + params['bucket']
        }
    )
    # print ("query response", start_query_response)
    return start_query_response

def athena_to_s3(sts, params, query, filename, rolename, accountId, max_execution = 50):

    credentialSTS = stsa.changeSTSAccount(sts, accountId, rolename)
    credentials = credentialSTS['Credentials']
    # print ("This is the credentials response: %s \n" % (credentials))

    client = session.client('athena', region_name=params["region"],
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],)

    s3 = boto3.resource('s3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],)

    execution = athena_query(client, params, query)
    execution_id = execution['QueryExecutionId']
    state = 'RUNNING'
    print(execution_id)

    while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
        max_execution = max_execution - 1
        response = client.get_query_execution(QueryExecutionId = execution_id)
        if 'QueryExecution' in response and \
                'Status' in response['QueryExecution'] and \
                'State' in response['QueryExecution']['Status']:
            state = response['QueryExecution']['Status']['State']
            print(state)
            if state == 'FAILED':
                return False
            elif state == 'SUCCEEDED':
                s3_path = response['QueryExecution']['ResultConfiguration']['OutputLocation']
                source_filename = re.findall('.*\/(.*)', s3_path)[0]
                csv.createAndWriteCsv(filename, '', '', '')
                try:
                    s3.Bucket(params['bucket']).download_file(source_filename, filename)
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("The object does not exist.")
                    else:
                        print(source_filename)
                        raise

                return filename

        time.sleep(2)
    return False
