# Ireland Climate Policy Atlas — Django dashboard

This project serves the existing interactive OECD CAPMF dashboard through a standard Django application. The bundled `policies.csv` is validated on the server and injected into the page; users can also validate another Ireland CAPMF CSV through the upload control.

## Run locally

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py manage.py runserver
```

Open <http://127.0.0.1:8000/>. A lightweight health endpoint is available at `/health/`.

## Configuration

- `CAPMF_CSV`: optional path to a different default CSV.
- `DJANGO_DEBUG`: set to `0` outside local development.
- `DJANGO_SECRET_KEY`: required in production.
- `DJANGO_ALLOWED_HOSTS`: comma-separated host names.

## Tests

```powershell
py manage.py test
```

For production, set the environment variables above and run the WSGI application at `policy_dashboard.wsgi:application`.
