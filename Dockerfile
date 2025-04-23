FROM public.ecr.aws/lambda/python:3.10

# Install the full TeX Live distribution and required utilities
RUN yum update -y && \
    yum install -y texlive-scheme-full less curl unzip && \
    yum clean all

# Copy the Lambda handler into the container
COPY app.py .

# Set the Lambda handler entry point
CMD ["app.lambda_handler"]