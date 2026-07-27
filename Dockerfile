FROM python:3.13

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    curl \
    gettext \
    ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY ./pyproject.toml /app/pyproject.toml
COPY ./uv.lock /app/uv.lock
RUN uv sync --locked --compile-bytecode

COPY ./app /app

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000"]
