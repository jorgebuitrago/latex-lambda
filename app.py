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

    # Define local file paths
    tex_path = "/tmp/document.tex"
    pdf_path = "/tmp/document.pdf"
    log_path = "/tmp/document.log"

    # Download the .tex file from S3
    s3.download_file(bucket, tex_key, tex_path)

    try:
        # Compile the .tex file using pdflatex
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", "/tmp", tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "LaTeX compilation failed",
                "stdout": e.stdout.decode(errors="ignore"),
                "stderr": e.stderr.decode(errors="ignore")
            })
        }

    # Determine output filenames and keys
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    pdf_key = f"{pdf_key_prefix}{custom_pdf_name}" if custom_pdf_name else f"{pdf_key_prefix}compiled_{timestamp}.pdf"
    log_key = pdf_key.replace(".pdf", ".log")

    # Upload PDF
    s3.upload_file(pdf_path, bucket, pdf_key)

    # Upload LaTeX log (if exists)
    if os.path.exists(log_path):
        s3.upload_file(log_path, bucket, log_key)
        log_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={"Bucket": bucket, "Key": log_key},
            ExpiresIn=3600
        )
    else:
        log_url = None

    # Generate PDF download link
    pdf_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={"Bucket": bucket, "Key": pdf_key},
        ExpiresIn=3600
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "PDF generated successfully",
            "pdf_url": pdf_url,
            "log_url": log_url
        })
    }
