import boto3
import os
import subprocess
import json
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse request body safely
    body = json.loads(event['body']) if isinstance(event.get("body"), str) else event
    bucket = body.get("bucket", os.environ.get("BUCKET_NAME"))
    tex_key = body.get("tex_key")
    pdf_key_prefix = body.get("pdf_key_prefix", "latex/outputs/")

    if not (bucket and tex_key):
        return {"statusCode": 400, "body": "Missing 'bucket' or 'tex_key'"}

    # File paths
    tex_path = "/tmp/document.tex"
    pdf_path = "/tmp/document.pdf"

    try:
        # Download the .tex file from S3
        s3.download_file(bucket, tex_key, tex_path)

        # Compile the .tex file
        subprocess.run(["pdflatex", "-output-directory", "/tmp", tex_path], check=True)

        # Upload compiled PDF
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        pdf_key = f"{pdf_key_prefix}compiled_{timestamp}.pdf"
        s3.upload_file(pdf_path, bucket, pdf_key)

        # Return a presigned URL for the PDF
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={"Bucket": bucket, "Key": pdf_key},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "PDF generated successfully",
                "url": url
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
