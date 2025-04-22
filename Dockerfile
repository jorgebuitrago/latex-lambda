FROM amazonlinux:2

# Install system dependencies
RUN yum -y update && yum -y install \
    perl wget curl tar gzip make xz unzip findutils which \
    python3 shadow-utils && yum clean all

# Manually install TinyTeX
WORKDIR /opt
RUN curl -LO https://yihui.org/tinytex/TinyTeX-1.tar.gz && \
    tar -xzf TinyTeX-1.tar.gz && \
    mv TinyTeX /opt/TinyTeX && \
    rm -f TinyTeX-1.tar.gz

# Set PATH
ENV PATH="/opt/TinyTeX/bin/x86_64-linuxmusl:$PATH"

# Pre-install essential LaTeX packages (choose what you need)
RUN /opt/TinyTeX/bin/*/tlmgr install \
    latex-bin \
    latexmk \
    geometry \
    fancyhdr \
    ulem \
    xcolor \
    microtype \
    fontspec \
    amsmath \
    hyperref \
    babel \
    enumitem \
    titlesec \
    pgf \
    tikzsymbols \
    booktabs \
    upquote \
    etoolbox \
    graphicx \
    tools

# Install AWS Lambda Runtime Interface Emulator (RIE)
ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/local/bin/aws-lambda-rie
RUN chmod +x /usr/local/bin/aws-lambda-rie

# Add a non-root user for Lambda compliance
RUN useradd -m lambdauser
WORKDIR /home/lambdauser

# Copy Lambda handler
COPY app.py .
RUN chown -R lambdauser:lambdauser /home/lambdauser
USER lambdauser

# Lambda runtime entrypoint
ENTRYPOINT ["/usr/local/bin/aws-lambda-rie", "python3", "-m", "awslambdaric"]
CMD ["app.lambda_handler"]
