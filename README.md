# Papelaria

Papelaria é um projeto de CMS pessoal utilizando o Wagtail e Django como bases. Os templates, atualmente, são criados com Bootstrap 5.

## Rodando localmente

É recomendado a execução para desenvolvimento utilizando o `docker` e `docker compose` devido ao fato de que as buscas utilizam o `PostgreSQL` como `backend` de pesquisa:

```bash
git clone https://github.com/EduardoJM/papelaria.git
cd papelaria
docker compose up --build
```

### Populando o banco de dados

Na mesma pasta que o `docker-compose.yml` execute:

```bash
docker compose exec cms uv run manage.py migrate
```

### Criando um usuário Admin

Na mesma pasta que o `docker-compose.yml` execute:

```bash
docker compose exec cms uv run manage.py createsuperuser
```

Preencha os dados para a criação da conta de admin e finalize.

### Acessando o site

Acesse:

```
http://localhost:8000/admin
```
