import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
import json

# Initialize OpenSearch client with Basic Authentication
es = OpenSearch(
    hosts=[{'host': 'search-photos-awoom3ry36u4qhdswftakubfae.us-east-1.es.amazonaws.com', 'port': 443}],
    http_auth=('Siddharth', 'temp_password@123'),  # Basic authentication
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def lambda_handler(event, context):
    # Log the entire event for inspection
    print("Event:", json.dumps(event))
    
    # Extract the search query from the event
    query_text = event.get('queryStringParameters', {}).get('q', '')
    print(f"Search query: {query_text}")

    # Initialize Lex V2 client
    lex = boto3.client('lexv2-runtime')
    
    # Call Lex V2 bot using recognize_text
    bot_id = 'EGOTWNPJRR'               # Replace with Lex V2 bot ID
    bot_alias_id = 'TSTALIASID'          # Replace with Lex V2 bot alias ID
    locale_id = 'en_US'                  # Replace with appropriate locale (e.g., 'en_US')
    
    lex_response = lex.recognize_text(
        botId=bot_id,
        botAliasId=bot_alias_id,
        localeId=locale_id,
        sessionId='user-session',
        text=query_text
    )
    
    print('Lex response:', lex_response)

    # Extract keywords from Lex response
    keywords = []
    if 'sessionState' in lex_response and 'intent' in lex_response['sessionState']:
        slots = lex_response['sessionState']['intent']['slots']
        keywords = [slots[slot]['value']['interpretedValue'] for slot in slots if slots[slot] and 'value' in slots[slot]]
    
    print(f"Extracted keywords: {keywords}")

    # Construct OpenSearch query
    search_query = {
        "query": {
            "bool": {
                "should": [{"match": {"labels": keyword}} for keyword in keywords]
            }
        }
    }
    print(f"OpenSearch query: {json.dumps(search_query)}")

    # Execute the search
    results = es.search(index="photos", body=search_query)
    print(f"Search results: {json.dumps(results)}")

    # Format and return results with CORS headers
    image_keys = [hit['_source']['objectKey'] for hit in results['hits']['hits']]
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps({
            "results": image_keys
        })
    }
