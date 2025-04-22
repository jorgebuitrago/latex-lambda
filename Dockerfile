FROM public.ecr.aws/lambda/python:3.10

# Install basic build tools and curl
RUN yum install -y curl perl wget tar gzip make xz && yum clean all

# Install TinyTeX from TUG
RUN curl -L -o /install-tinytex.sh https://yihui.org/tinytex/install-bin-unix.sh && \
    chmod +x /install-tinytex.sh && \
    ./install-tinytex.sh && \
    ln -s /root/.TinyTeX/bin/*/pdflatex /usr/local/bin/pdflatex

# Copy your function code
COPY app.py .

# Set environment variable so TinyTeX works in Lambda
ENV PATH="/root/.TinyTeX/bin/x86_64-linuxmusl:$PATH"

CMD ["app.lambda_handler"]