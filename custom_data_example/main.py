import json
import typer
from typing import List, Optional
from typing_extensions import Annotated

from custom_data_example.util import cortex_request

app = typer.Typer(
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)

@app.callback()
def global_callback(
    ctx: typer.Context,
    api_key: str = typer.Option(None, "--api-key", "-k", help="API key", envvar="CORTEX_API_KEY"),
    base_url: str = typer.Option("https://api.getcortexapp.com", "--url", "-u", help="Base URL for the API", envvar="CORTEX_BASE_URL"),
):
    if not api_key:
        raise typer.BadParameter("API key is required, either via --api-key flag or CORTEX_API_KEY environment variable")
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj['API_KEY'] = api_key
    ctx.obj['BASE_URL'] = base_url

@app.command()
def add(
    ctx: typer.Context,
    entity_tags: Annotated[Optional[List[str]], typer.Option("--tags", "-t", help="The entity tags to set custom data on")] = None,
    keys: Annotated[Optional[List[str]], typer.Option("--keys", "-k", help="The keys to set in custom data")] = None,
    values: Annotated[Optional[List[str]], typer.Option("--values", "-v", "The values for the keys. If a value is JSON it will get parsed to an object.")] = None,
):
    """
    Example of API call to bulk add custom data to entities
    """
    if not entity_tags:
        raise typer.BadParameter("At least one entity tag is required")
    if not keys:
        raise typer.BadParameter("At least one key is required")
    if not values:
        raise typer.BadParameter("At least one value is required")
    
    if len(keys) != len(values):
        raise typer.BadParameter("Keys and values must have the same length")
    kvpairs = []
    for key, value in zip(keys, values):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            pass
        kvpairs.append({"key": key, "value": value})

    payload = {
        "values": {
            entity_tag: kvpairs
            for entity_tag in entity_tags
        }
    }
    
    response = cortex_request(
        method="PUT",
        endpoint="/api/v1/catalog/custom-data",
        data=payload,
        api_key=ctx.obj['API_KEY'],
        base_url=ctx.obj['BASE_URL'],
    )

@app.command()
def remove(
    ctx: typer.Context,
    entity_tags: Annotated[Optional[List[str]], typer.Option("--tags", "-t", help="The entity tags to delete custom data from")] = None,
    keys: Annotated[Optional[List[str]], typer.Option("--keys", "-k", help="The keys to delete in custom data")] = None,
):
    """
    Example of API call to remove custom data from entities
    """
    if not entity_tags:
        raise typer.BadParameter("At least one entity tag is required")
    if not keys:
        raise typer.BadParameter("At least one key is required")

    for entity_tag in entity_tags:
        for key in keys:
            cortex_request(
                method="DELETE",
                endpoint=f"/api/v1/catalog/{entity_tag}/custom-data",
                params={"key": key},
                api_key=ctx.obj['API_KEY'],
                base_url=ctx.obj['BASE_URL'],
            )

if __name__ == "__main__":
    app()
