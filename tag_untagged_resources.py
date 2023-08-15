import boto3
import time
import botocore

# Initialize the AWS resources
regions = ['eu-central-1']  # Add more regions as needed

def get_all_resources(tag_editor_client):
    all_resources = []
    next_token = None

    while True:
        try:
            if next_token:
                response = api_request_with_retry(tag_editor_client, tag_editor_client.get_resources, PaginationToken=next_token)
            else:
                response = api_request_with_retry(tag_editor_client, tag_editor_client.get_resources)

            all_resources.extend(response.get('ResourceTagMappingList', []))
            next_token = response.get('PaginationToken')

            if not next_token:
                break

        except Exception as e:
            print(f"Error getting resources: {str(e)}")
            break

    return all_resources


def find_resources_missing_costcenter(region, account_id):
    try:
        session = boto3.Session(region_name=region)

        # Initialize AWS Tag Editor client
        tag_editor_client = session.client('resourcegroupstaggingapi')

        # Get all resources across all pages
        all_resources = get_all_resources(tag_editor_client)

        # Filter resources missing 'CostCenter' tag and exclude SSM sessions
        untagged_resources = [
            {
                "ResourceARN": resource["ResourceARN"],
                "AccountId": account_id,
                "Region": region
            }
            for resource in all_resources
            if (not any(tag['Key'] == 'CostCenter' for tag in resource.get('Tags', [])))
            and (not resource['ResourceARN'].startswith('arn:aws:ssm'))
            and (not resource['ResourceARN'].startswith(f'arn:aws:elasticloadbalancing:{region}:{account_id}:listener'))
        ]

        return untagged_resources

    except Exception as e:
        print(f"Error finding resources in {region}: {str(e)}")
        return []


def tag_resources_with_costcenter(region, untagged_resources):
    try:
        session = boto3.Session(region_name=region)

        # Initialize AWS Tag Editor client
        tag_editor_client = session.client('resourcegroupstaggingapi')

        for resource in untagged_resources:
            resource_name = None
            for tag in resource.get('Tags', []):
                if tag['Key'] == 'Name':
                    resource_name = tag['Value']
                    break
            
            if not resource_name:
                # If 'Name' tag is missing, generate a human-readable tag value
                resource_name = f"Resource-{resource['ResourceARN'].split(':')[-1]}"

            tags = {
                'CostCenter': resource_name
            }
            api_request_with_retry(tag_editor_client, tag_editor_client.tag_resources, ResourceARNList=[resource['ResourceARN']], Tags=tags)
            print(f"Tagged resource {resource['ResourceARN']} with CostCenter: {resource_name}")

            # Introduce a delay between requests (e.g., 1 second)
            time.sleep(1)

    except Exception as e:
        print(f"Error tagging resources in {region}: {str(e)}")

def api_request_with_retry(client, func, **kwargs):
    max_retries = 5
    retry_delay = 2  # seconds
    retries = 2

    while retries < max_retries:
        try:
            response = func(**kwargs)
            return response
        except botocore.exceptions.ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 429:
                print(f"Rate limited, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retries += 1
                retry_delay *= 2  # Exponential backoff
            else:
                raise

    raise Exception("API request failed after retries")


def write_untagged_resources_to_file(filename, untagged_resources):
    with open(filename, 'w') as file:
        for resource in untagged_resources:
            file.write(f"Resource ARN: {resource['ResourceARN']}\n")
            # Add more information as needed

def main():
    for region in regions:
        account_id = boto3.client('sts').get_caller_identity().get('Account')
        untagged_resources = find_resources_missing_costcenter(region,account_id)
        if untagged_resources:
            write_untagged_resources_to_file(f"allresources_{region}.txt", untagged_resources)
            tag_resources_with_costcenter(region, untagged_resources)
        else:
            print(f"No untagged resources found in {region}")

if __name__ == "__main__":
    main()
