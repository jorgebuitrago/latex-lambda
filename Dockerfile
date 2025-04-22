FROM public.ecr.aws/lambda/python:3.10

RUN yum install -y texlive-latex texlive-xetex texlive-geometry texlive-fancyhdr && \
    yum install -y less curl unzip && \
    yum clean all

COPY app.py .

CMD ["app.lambda_handler"]