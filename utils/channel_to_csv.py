import click
import requests
import pandas as pd
import json
import os


def get_json(url, max_count=1000):
    """ Fetch requested number of results. """

    results = []
    retrieved = 0

    while url and (retrieved < max_count):
        try:
            click.echo(".", nl=False)
            json_data = requests.get(url).json()
            retrieved = retrieved + len(json_data["results"])
            results.extend(json_data["results"])
            url = json_data["next"]
        except Exception as e:
            click.echo(f"Error: {e}")
            break

    # Final line break
    click.echo("")
    return results[:max_count]


def json_to_csv(data, filename):
    try:
        pd.read_json(json.dumps(data)).to_csv(filename)
    except Exception as e:
        click.echo(e)


@click.command()
@click.argument("channel_url")
@click.argument("filename")
@click.option(
    "--count",
    default=1000,
    prompt="Number of results.",
    help="Maximum number of results to fetch (if available).",
)
def fetch(channel_url, filename, count):
    """ Store CHANNEL_URL measurements to FILENAME. """
    json_data = get_json(channel_url, count)

    if not json_data:
        click.echo("Error fetching data")
        return

    click.echo("Retrieved {} results from {}".format(len(json_data), channel_url))

    json_to_csv(json_data, filename)
    click.echo("Created file {}".format(os.path.abspath(filename)))


if __name__ == "__main__":
    fetch()
