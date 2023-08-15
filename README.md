# AWS Resource Tagger

This Python script helps you identify and tag untagged AWS resources with a 'CostCenter' tag.

## Description

This script uses the AWS SDK (boto3) to search for untagged resources across specified AWS regions. It then tags these untagged resources with a 'CostCenter' tag using the AWS Tag Editor service.

## Prerequisites

- Python 3.6 or later
- AWS CLI configured with appropriate permissions
- `boto3` library installed (`pip install boto3`)

## Usage

1. Clone this repository to your local machine.

2. Navigate to the cloned repository directory.

3. Open the script file `tag_untagged_resources.py` and update the following variables:

   - `regions`: List of AWS regions to search for untagged resources.

4. Run the script:

python tag_untagged_resources.py


The script will identify untagged resources in the specified regions and apply the specified tag.

5. Optionally, review the generated `untagged_resources_{region}.txt` files to see the list of untagged resources in each region.

## Notes

- The script may take some time to execute, depending on the number of resources in your AWS account.

- The script includes rate limiting and backoff strategies to handle potential API throttling. You can adjust the `max_retries` and `retry_delay` values in the script if needed.

## Disclaimer

This script interacts with your AWS resources and applies tags. Use it responsibly and ensure you have the necessary permissions to make changes to your AWS environment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

