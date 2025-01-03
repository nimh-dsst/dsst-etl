FROM --platform=linux/amd64 condaforge/mambaforge:24.3.0-0
SHELL ["/bin/bash", "--login", "-c"]
# Set working directory
WORKDIR /app

# Install pdftotext
RUN apt-get update && apt-get install -y poppler-utils

COPY environment.yaml /app

# Create the environment
RUN conda env create -f environment.yaml

# Ensure the conda environment is activated
RUN echo "source /opt/conda/etc/profile.d/conda.sh && conda activate osm" | tee -a ~/.bashrc /etc/profile /etc/profile.d/conda.sh /etc/skel/.bashrc /etc/skel/.profile > /dev/null

RUN R -e 'devtools::install_github("quest-bih/oddpub",ref="c5b091c7e82ed6177192dc380a515b3dc6304863")'

# # Copy the project files and install the package
COPY app.py /app

# Make entrypoint etc. convenient for users
COPY _entrypoint.sh /usr/local/bin/_entrypoint.sh

# Make _entrypoint.sh executable
RUN chmod +x /usr/local/bin/_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh"]

CMD ["fastapi", "dev", "--host", "0.0.0.0", "--port", "8071"]
