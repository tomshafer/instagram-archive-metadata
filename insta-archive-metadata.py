"""Tag an Instagram archive with metadata"""

import json
import logging
import os
import shlex
import subprocess as sp
import uuid
from datetime import datetime
from typing import Any, Sized

import click
import pytz
from tqdm.auto import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler("ig.log")],
    )


def p(collection: Sized) -> str:
    return "s" if len(collection) != 1 else ""


def collect_images(source: str) -> list[dict[str, Any]]:
    meta = []

    target = os.path.join(source, "content", "posts_1.json")
    if os.path.exists(target):
        with open(target) as f:
            meta += [img for item in json.load(f) for img in item["media"]]

    target = os.path.join(source, "content", "profile_photos.json")
    if os.path.exists(target):
        with open(target) as f:
            meta += json.load(f)["ig_profile_picture"]

    target = os.path.join(source, "content", "stories.json")
    if os.path.exists(target):
        with open(target) as f:
            meta += json.load(f)["ig_stories"]

    # Rewrite paths
    for m in meta:
        m["uri"] = os.path.join(source, m["uri"])

    return meta


def tag_and_copy_item(item: dict[str, Any], destdir: str) -> None:
    new_uuid = uuid.uuid4()
    dest_path = os.path.join(destdir, f"{new_uuid}{os.path.splitext(item['uri'])[-1]}")

    timestamp = datetime.fromtimestamp(item["creation_timestamp"])
    timestamp = timestamp.astimezone(pytz.timezone("America/New_York"))

    # NB: ASCII so we've lost the emoji
    description: str = item.get("title", "").strip()

    try:
        lat = list(item["media_metadata"].values())[0]["exif_data"][0]["latitude"]
        lon = list(item["media_metadata"].values())[0]["exif_data"][0]["longitude"]
    except KeyError:
        lat, lon = None, None

    run_exiftool(
        source=item["uri"],
        dest=dest_path,
        timestamp=timestamp,
        description=description,
        latitude=lat,
        longitude=lon,
    )

    run_setfile(
        path=dest_path,
        timestamp=timestamp,
    )


def run_exiftool(
    source: str,
    dest: str,
    timestamp: datetime,
    description: str,
    latitude: str,
    longitude: str,
) -> None:

    cmd = "exiftool"

    if timestamp:
        value = timestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
        cmd += f" -DatetimeOriginal='{value}'"
        cmd += f" -DatetimeDigitized='{value}'"

    if description:
        cmd += f" -ImageDescription={shlex.quote(description)}"

    if latitude:
        cmd += f" -GPSLatitude='{latitude}'"

    if longitude:
        cmd += f" -GPSLongitudeRef=W -GPSLongitude='{longitude}'"

    cmd += f' -o "{dest}" "{source}"'

    logger.info(cmd)
    job = sp.run(shlex.split(cmd), stderr=sp.PIPE, check=True, stdout=sp.DEVNULL)

    if job.stderr:
        logger.info(f"STDERR = {job.stderr.decode('utf8')}")


def run_setfile(path: str, timestamp: datetime) -> None:
    value = timestamp.strftime("%m/%d/%y %H:%M:%S %P")
    cmd = f"SetFile -d '{value}' {shlex.quote(path)}"
    job = sp.run(cmd, shell=True, check=True, stderr=sp.PIPE, stdout=sp.DEVNULL)

    if job.stderr:
        logger.info(f"STDERR = {job.stderr.decode('utf8')}")


@click.command()
@click.option(
    "--source",
    "-s",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Instagram archive root.",
)
@click.option(
    "--output",
    "-o",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Export directory.",
)
def main(source: str, output: str) -> None:
    setup_logging()
    logger.info(f"source = {source}")
    logger.info(f"output = {output}")

    media = collect_images(source)
    logger.info(f"Collected {len(media)} item{p(media)}")

    destdir = os.path.join(output, datetime.now().strftime("%Y%m%d_%H%M%S"))
    logger.info(f"Writing items to {destdir}")

    for item in tqdm(media, unit="item"):
        tag_and_copy_item(item, destdir)


if __name__ == "__main__":
    main()
