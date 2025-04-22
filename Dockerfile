FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y texlive-scheme-full less curl unzip && \
    yum clean all

COPY app.py .

CMD ["app.lambda_handler"]