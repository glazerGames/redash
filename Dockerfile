# Frontend build stage
FROM node:18-bookworm AS frontend-builder

# Install Yarn globally
RUN npm install --global --force yarn@1.22.22

# Environment variables for Cypress and Puppeteer (for headless testing)
ENV CYPRESS_INSTALL_BINARY=0
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

# Create a non-root user to run the frontend build
RUN useradd -m -d /frontend redash
USER redash

# Set the working directory for the frontend
WORKDIR /frontend
COPY --chown=redash package.json yarn.lock .yarnrc /frontend/
COPY --chown=redash viz-lib /frontend/viz-lib
COPY --chown=redash scripts /frontend/scripts

# Set environment for code coverage, defaults to 'test' if enabled
ARG code_coverage
ENV BABEL_ENV=${code_coverage:+test}

# Avoid issues with QEMU emulation during multi-platform builds
RUN yarn config set network-timeout 300000

# Build the frontend assets unless skip_frontend_build is set
ARG skip_frontend_build
RUN if [ "x$skip_frontend_build" = "x" ] ; then yarn --frozen-lockfile --network-concurrency 1; fi

# Copy client files and Webpack config
COPY --chown=redash client /frontend/client
COPY --chown=redash webpack.config.js /frontend/

# Build the frontend if skip_frontend_build is not set
RUN <<EOF
  if [ "x$skip_frontend_build" = "x" ]; then
    yarn build
  else
    mkdir -p /frontend/client/dist
    touch /frontend/client/dist/multi_org.html
    touch /frontend/client/dist/index.html
  fi
EOF

# Python and backend build stage
FROM python:3.10-slim-bookworm

# Expose the port for Redash (default 5000)
EXPOSE 5000

# Create a non-root user for the backend
RUN useradd --create-home redash

# Install required system packages for Redash and its dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  pkg-config \
  curl \
  gnupg \
  build-essential \
  pwgen \
  libffi-dev \
  sudo \
  git-core \
  libkrb5-dev \
  libpq-dev \
  g++ unixodbc-dev \
  xmlsec1 \
  libssl-dev \
  default-libmysqlclient-dev \
  freetds-dev \
  libsasl2-dev \
  unzip \
  libsasl2-modules-gssapi-mit && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Download and install Microsoft ODBC driver and Databricks ODBC driver
ARG TARGETPLATFORM
ARG databricks_odbc_driver_url=https://databricks-bi-artifacts.s3.us-east-2.amazonaws.com/simbaspark-drivers/odbc/2.6.26/SimbaSparkODBC-2.6.26.1045-Debian-64bit.zip
RUN <<EOF
  if [ "$TARGETPLATFORM" = "linux/amd64" ]; then
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update
    ACCEPT_EULA=Y apt-get install  -y --no-install-recommends msodbcsql18
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    curl "$databricks_odbc_driver_url" --location --output /tmp/simba_odbc.zip
    chmod 600 /tmp/simba_odbc.zip
    unzip /tmp/simba_odbc.zip -d /tmp/simba
    dpkg -i /tmp/simba/*.deb
    printf "[Simba]\nDriver = /opt/simba/spark/lib/64/libsparkodbc_sb64.so" >> /etc/odbcinst.ini
    rm /tmp/simba_odbc.zip
    rm -rf /tmp/simba
  fi
EOF

# Set working directory and install Poetry
WORKDIR /app

ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/etc/poetry
ENV POETRY_VIRTUALENVS_CREATE=false
RUN curl -sSL https://install.python-poetry.org | python3 -

# Clear any cached poetry artifacts
RUN /etc/poetry/bin/poetry cache clear pypi --all

# Copy pyproject.toml and poetry.lock to the working directory
COPY pyproject.toml poetry.lock ./

# Set default values for install groups and poetry options
ARG install_groups="main,all_ds,dev"
ARG POETRY_OPTIONS="--no-root --no-interaction --no-ansi"

# Install dependencies
RUN /etc/poetry/bin/poetry install --only $install_groups $POETRY_OPTIONS --verbose

# Copy the rest of the application and frontend build into the container
COPY --chown=redash . /app
COPY --from=frontend-builder --chown=redash /frontend/client/dist /app/client/dist

# Change ownership to 'redash' user and set the working directory
RUN chown redash /app
USER redash

# Set entrypoint and default command for the application
ENTRYPOINT ["/app/bin/docker-entrypoint"]
CMD ["server"]
