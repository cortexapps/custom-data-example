import json
import requests
import typer
import yaml

def cortex_request(method: str, endpoint: str, data: dict = None, params: dict = {}, api_key: str = None, base_url: str = 'https://api.getcortexapp.com'):
    yaml_endpoints = {
        "/api/v1/open-api": "application/openapi;charset=utf-8",
        "/api/v1/scorecards/descriptor": "application/yaml;charset=utf-8",
    }
    if not api_key:
        raise typer.BadParameter("API key is required")
    if endpoint in yaml_endpoints:
        content_type = yaml_endpoints[endpoint]
        data_str = yaml.dump(data, sort_keys=False)
    else:
        content_type = "application/json"
        data_str = json.dumps(data)

    url = '/'.join([base_url.rstrip('/'), endpoint.lstrip('/')])
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": content_type,
    }

    if data is None:
        data_str = None
    response = requests.request(method, url, headers=headers, params=params, data=data_str)
    if not response.ok:
        print(f"Request failed with status code {response.status_code}")
        print(response.text)
    response.raise_for_status()
    try:
        return response.json()
    except json.JSONDecodeError:
        return response.text
