FROM public.ecr.aws/lambda/python:3.10

# Install required tools for TinyTeX and PDF compilation
RUN yum install -y curl wget perl tar gzip make xz unzip findutils && yum clean all

# Install TinyTeX
RUN curl -L -o /install-tinytex.sh https://yihui.org/tinytex/install-bin-unix.sh && \
    chmod +x /install-tinytex.sh && \
    ./install-tinytex.sh && \
    ln -s /root/.TinyTeX/bin/*/pdflatex /usr/local/bin/pdflatex

# Set environment path
ENV PATH="/root/.TinyTeX/bin/x86_64-linuxmusl:$PATH"

# Copy your Lambda function
COPY app.py .

# Lambda entrypoint
CMD ["app.lambda_handler"]
