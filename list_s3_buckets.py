#!/usr/bin/env python3

import boto3

def list_s3_buckets():
    """
    List all S3 buckets in the AWS account
    """
    # Create an S3 client
    s3_client = boto3.client('s3')
    
    # Call S3 to list current buckets
    response = s3_client.list_buckets()
    
    # Get a list of all bucket names from the response
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    
    print("S3 Buckets:")
    for i, bucket_name in enumerate(buckets, 1):
        print(f"{i}. {bucket_name}")
    
    return buckets

if __name__ == "__main__":
    list_s3_buckets()
