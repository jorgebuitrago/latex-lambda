import boto3
import os
import subprocess
import json
from datetime import datetime

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parse the incoming payload (body might be a JSON string)
    body = json.loads(event['body']) if isinstance(event.get("body"), str) else event

    # Mandatory parameters for S3 access
    bucket = body.get("bucket", os.environ.get("BUCKET_NAME"))
    tex_key = body.get("tex_key")

    # Optional customization for output file
    pdf_key_prefix = body.get("pdf_key_prefix", "pdfs/")
    custom_pdf_name = body.get("pdf_key_name", "")

    if not (bucket and tex_key):
        return {
            "statusCode": 400,
            "body": "Missing 'bucket' or 'tex_key'"
        }

    # Define local file paths for .tex and .pdf
    tex_path = "/tmp/document.tex"
    pdf_path = "/tmp/document.pdf"

    # Download the .tex file from S3
    s3.download_file(bucket, tex_key, tex_path)

    try:
        # Compile the .tex file using pdflatex
        subprocess.run(["pdflatex", "-output-directory", "/tmp", tex_path], check=True)
    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "LaTeX compilation failed",
                "stdout": e.stdout.decode(errors="ignore"),
                "stderr": e.stderr.decode(errors="ignore")
            })
        }

    # Determine the PDF key (location and name in S3)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    if custom_pdf_name:
        pdf_key = f"{pdf_key_prefix}{custom_pdf_name}"
    else:
        pdf_key = f"{pdf_key_prefix}compiled_{timestamp}.pdf"

    # Upload the compiled PDF back to S3
    s3.upload_file(pdf_path, bucket, pdf_key)

    # Generate a presigned URL for the PDF
    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={"Bucket": bucket, "Key": pdf_key},
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "PDF generated successfully",
            "url": presigned_url
        })
    }
