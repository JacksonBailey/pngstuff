from enum import Enum
from io import IOBase
from typing import TypeVar
import click


_File = type[IOBase | click.utils.LazyFile]


class Action(Enum):
    DUMP = "dump"
    STRIP = "strip"


_actions = list(map(lambda e: e.value, Action))


@click.command()
@click.option(
    "-i",
    "--input",
    type=click.File(mode="rb"),
    required=True,
    prompt=False,
    help="Input image",
)
@click.option(
    "-o",
    "--output",
    type=click.File(mode="wb"),
    required=False,
    prompt=False,
    help="Output location",
)
@click.option(
    "-a",
    "--action",
    type=click.Choice(choices=_actions, case_sensitive=False),
    required=True,
    prompt=False,
    help="Action to take",
    default="dump",
)
def cli_command(input: _File, output: _File, action: str) -> None:
    pngstuff_action(input=input, output=output, action=Action(action))


def pngstuff_action(input: IOBase, output: _File, action: Action) -> None:
    match action:
        case Action.DUMP:
            dump(input=input)
        case Action.STRIP:
            strip(input=input, output=output)


def dump(input: _File) -> None:
    header = input.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"
    while True:
        chunk_length = int.from_bytes(input.read(4), byteorder="big")
        if not chunk_length:
            break
        chunk_type = input.read(4)
        chunk_data = input.read(chunk_length)
        chunk_crc = input.read(4)
        if chunk_type == b"IDAT":
            click.echo(
                f"{chunk_type}\t{chunk_length}\t(omitted image data)\t{chunk_crc}"
            )
        else:
            click.echo(f"{chunk_type}\t{chunk_length}\t{chunk_data}\t{chunk_crc}")


def strip(input: _File, output: _File) -> None:
    header = input.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"
    output.write(header)
    while True:
        chunk_length_bytes = input.read(4)
        chunk_length = int.from_bytes(chunk_length_bytes, byteorder="big")
        if not chunk_length:
            break
        chunk_type = input.read(4)
        chunk_data = input.read(chunk_length)
        chunk_crc = input.read(4)
        if chunk_type not in [b"IHDR", b"IDAT"]:
            click.echo(f"{chunk_type}\t{chunk_length}\t{chunk_crc}")
        else:
            output.write(chunk_length_bytes)
            output.write(chunk_type)
            output.write(chunk_data)
            output.write(chunk_crc)
