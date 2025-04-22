FROM public.ecr.aws/lambda/python:3.10

# Install working LaTeX components
RUN yum install -y texlive texlive-xetex less curl unzip && \
    yum clean all

# Copy Lambda handler
COPY app.py .

CMD ["app.lambda_handler"]
