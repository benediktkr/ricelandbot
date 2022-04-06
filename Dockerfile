FROM python:3.9-bullseye as base
MAINTAINER ben <ben@sudo.is>

ENV DEBIAN_FRONTEND noninteractive
ENV TZ UTC
ENV TERM=xterm-256color

ARG UID=1300
ENV PATH "$PATH:/home/user/.local/bin"

WORKDIR /ricelandbot
RUN useradd -m -u ${UID} -s /bin/bash user && \
        chown user:user /ricelandbot
USER user
RUN python3 -m pip install --upgrade pip

FROM base as builder
USER user
RUN python3 -m pip install poetry

COPY pyproject.toml /ricelandbot
COPY poetry.lock /ricelandbot
COPY .flake8 /ricelandbot/
RUN poetry install --no-interaction --ansi --no-root

# copy the tests and code after installing dependencies
COPY tests /ricelandbot/tests/
COPY ricelandbot /ricelandbot/ricelandbot/
COPY README.md /ricelandbot/README.md

RUN poetry install --no-interaction --ansi

RUN poetry run pytest
RUN poetry run flake8
RUN poetry run isort . --check

RUN poetry build --no-interaction --ansi
RUN poetry export --without-hashes > /ricelandbot/requirements.txt

FROM base as final

COPY --from=builder /ricelandbot/requirements.txt /tmp
RUN python3 -m pip install -r /tmp/requirements.txt

COPY --from=builder /ricelandbot/dist/ricelandbot-*.tar.gz /tmp
RUN python3 -m pip install /tmp/ricelandbot-*.tar.gz && \
        rm -v /tmp/ricelandbot-*.tar.gz /tmp/requirements.txt

HEALTHCHECK --start-period=5s --interval=15s --timeout=1s \
        CMD pgrep ricelandbot
CMD ["ricelandbot"]
