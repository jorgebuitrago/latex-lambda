FROM amazonlinux:2

# Install system dependencies for TinyTeX and AWS Lambda compatibility
RUN yum -y update && \
    yum -y install \
      perl \
      wget \
      curl \
      tar \
      gzip \
      make \
      xz \
      unzip \
      findutils \
      which \
      python3 \
      shadow-utils && \
    yum clean all

# Install TinyTeX (latest TeX Live)
# Set HOME so TinyTeX knows where to install
ENV HOME=/root

# Download and install TinyTeX (robust version)
RUN curl -L -o install-tinytex.sh https://yihui.org/tinytex/install-bin-unix.sh && \
    chmod +x install-tinytex.sh && \
    ./install-tinytex.sh --admin --no-path && \
    ln -s /root/.TinyTeX/bin/*/pdflatex /usr/local/bin/pdflatex

# Set PATH so pdflatex is always found
ENV PATH="/root/.TinyTeX/bin/x86_64-linuxmusl:$PATH"

# Install essential LaTeX packages you'll likely need
RUN /root/.TinyTeX/bin/*/tlmgr install \
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

# Create a non-root Lambda-compatible user
RUN useradd -m lambdauser
WORKDIR /home/lambdauser

# Copy Lambda handler
COPY app.py .
RUN chown -R lambdauser:lambdauser /home/lambdauser
USER lambdauser

# Lambda runtime entrypoint
ENTRYPOINT ["/usr/local/bin/aws-lambda-rie", "python3", "-m", "awslambdaric"]
CMD ["app.lambda_handler"]