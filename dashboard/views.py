import csv
import html
import json
from functools import lru_cache

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .services import MAX_BYTES, parse_csv


@lru_cache(maxsize=2)
def _read_dataset(path_string, modified_ns):
    path = settings.POLICIES_CSV.__class__(path_string)
    return parse_csv(path.read_bytes(), path.name)


def read_default_dataset():
    path = settings.POLICIES_CSV
    return _read_dataset(str(path), path.stat().st_mtime_ns)


def json_response(payload, status=200):
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store"
    return response


@require_GET
@ensure_csrf_cookie
def index(request):
    try:
        payload = read_default_dataset()
        safe_json = json.dumps(payload, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        response = render(request, "dashboard/index.html", {"initial_data": safe_json})
        response["Cache-Control"] = "no-store"
        return response
    except (OSError, ValueError, csv.Error) as error:
        return HttpResponse(
            f"<h1>Could not load the dashboard</h1><p>{html.escape(str(error))}</p>",
            status=500,
        )


@require_GET
def dataset(request):
    try:
        payload = read_default_dataset()
        return json_response(payload)
    except (OSError, ValueError, csv.Error) as error:
        return json_response({"error": str(error)}, status=422)


@require_POST
def validate_upload(request):
    uploaded = request.FILES.get("file")
    if uploaded is None:
        return json_response({"error": "Choose a CSV file."}, status=400)
    if uploaded.size > MAX_BYTES:
        return json_response({"error": "The CSV must be smaller than 12 MiB."}, status=413)
    try:
        return json_response(parse_csv(uploaded.read(MAX_BYTES + 1), uploaded.name))
    except (UnicodeDecodeError, ValueError, csv.Error) as error:
        return json_response({"error": str(error)}, status=422)


@require_GET
def health(request):
    return json_response({"status": "ok"})
