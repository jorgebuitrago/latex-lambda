import os
import subprocess
import base64
import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
bucket_name = os.environ.get("BUCKET_NAME", "")  # Set this in Lambda config

def lambda_handler(event, context):
    # Get LaTeX string
    body = json.loads(event["body"])
    tex_content = body.get("tex", "")

    # Save it to /tmp
    tex_path = "/tmp/document.tex"
    pdf_path = "/tmp/document.pdf"
    with open(tex_path, "w") as f:
        f.write(tex_content)

    try:
        subprocess.run(["pdflatex", "-output-directory", "/tmp", tex_path], check=True)

        # Upload to S3 (optional but better than base64 for large PDFs)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        s3_key = f"pdfs/document_{timestamp}.pdf"
        s3.upload_file(pdf_path, bucket_name, s3_key)

        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 1 hour
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "PDF generated successfully",
                "url": presigned_url
            })
        }

    except subprocess.CalledProcessError:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "LaTeX compilation failed"})
        }
