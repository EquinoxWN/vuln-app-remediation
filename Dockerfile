# Lab image: runs the test suite (reference exploits) with no network. CI-only; never published.
FROM python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /lab
COPY pyproject.toml README.md ./
COPY src ./src
COPY tests ./tests
COPY docs/writeups ./docs/writeups
RUN pip install --no-cache-dir . "pytest>=8" "pytest-timeout>=2.3" \
    && useradd --uid 10001 --no-create-home lab
USER 10001
HEALTHCHECK NONE
CMD ["vuln-lab", "flaws"]
