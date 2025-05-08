import boto3
import json
import datetime

s3 = boto3.client('s3')

BUCKET_NAME = 'vcflicensing'
SOURCE_PATH = 'VMwareLicenseReport/content/'
DESTINATION_PATH = 'VMwareLicenseReport/customers/'

# Default files
PREPEND_FILE = '0-intro'   # added before user files
APPEND_FILE = '1-footer'   # added after user files

def lambda_handler(event, context):
    try:
        # Parse the input body
        body = json.loads(event['body']) if 'body' in event else event
        filenames = body.get('filenames')
        customer_name = body.get('customer_name')

        # Basic validation
        if not filenames or not isinstance(filenames, list) or not customer_name:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input. Expected JSON with "filenames" (array) and "customer_name" (string).'})
            }

        aggregated_content = ''

        # 1️⃣ Add PREPEND_FILE first
        prepend_key = f"{SOURCE_PATH}{PREPEND_FILE}"
        try:
            print(f"Fetching {prepend_key} from {BUCKET_NAME}")
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=prepend_key)
            file_content = obj['Body'].read().decode('utf-8')
            aggregated_content += file_content + '\n'
        except Exception as e:
            print(f"Error fetching {prepend_key}: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to fetch file {prepend_key}. Error: {str(e)}'})
            }

        # 2️⃣ Add user-provided files
        for filename in filenames:
            source_key = f"{SOURCE_PATH}{filename}"
            try:
                print(f"Fetching {source_key} from {BUCKET_NAME}")
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=source_key)
                file_content = obj['Body'].read().decode('utf-8')
                aggregated_content += file_content + '\n'
            except Exception as e:
                print(f"Error fetching {source_key}: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Failed to fetch file {source_key}. Error: {str(e)}'})
                }

        # 3️⃣ Add APPEND_FILE last
        append_key = f"{SOURCE_PATH}{APPEND_FILE}"
        try:
            print(f"Fetching {append_key} from {BUCKET_NAME}")
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=append_key)
            file_content = obj['Body'].read().decode('utf-8')
            aggregated_content += file_content + '\n'
        except Exception as e:
            print(f"Error fetching {append_key}: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to fetch file {append_key}. Error: {str(e)}'})
            }

        # Prepare output path with .tex extension
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        output_filename = f"{customer_name}-{timestamp}.tex"
        destination_key = f"{DESTINATION_PATH}{customer_name}/{output_filename}"

        # Upload aggregated file to destination path
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=destination_key,
            Body=aggregated_content.encode('utf-8')
        )

        full_s3_path = f"s3://{BUCKET_NAME}/{destination_key}"
        print(f"Aggregated content successfully uploaded to {full_s3_path}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Files aggregated successfully.',
                'output_file_path': full_s3_path
            })
        }

    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
