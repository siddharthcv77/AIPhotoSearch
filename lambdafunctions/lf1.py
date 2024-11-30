import boto3
import json
from datetime import datetime
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

# Initialize AWS clients
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    username = 'Siddharth'
    password = 'temp_password@123'

    # OpenSearch client with Basic Authentication
    es = OpenSearch(
        hosts=[{'host': 'search-photos-awoom3ry36u4qhdswftakubfae.us-east-1.es.amazonaws.com', 'port': 443}],
        http_auth=(username, password),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
   
    # Extract bucket and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    print(f"Processing file from Bucket: {bucket}, Object Key: {object_key}")

    # Detect labels using Rekognition
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': object_key}},
        MaxLabels=10
    )
    labels = [label['Name'] for label in response['Labels']]
    print(f"Detected labels: {labels}")
    
    # Retrieve custom labels from S3 metadata
    metadata = s3.head_object(Bucket=bucket, Key=object_key)
    custom_labels = metadata.get('Metadata', {}).get('x-amz-meta-customlabels', "")
    if custom_labels:
        labels.extend(custom_labels.split(", "))
    print(f"Final labels including custom labels: {labels}")

    # Prepare JSON object for OpenSearch
    document = {
        "objectKey": object_key,
        "bucket": bucket,
        "createdTimestamp": datetime.utcnow().isoformat(),
        "labels": labels
    }
    print(f"Document to be indexed in OpenSearch: {document}")
    
    # Index the document in OpenSearch
    es.index(index="photos", id=object_key, body=document)
    print("Document indexed successfully.")
    
    return {"status": "success"}
