from enum import Enum
from io import IOBase
import click


class Action(Enum):
    DUMP = "dump"


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
    "-a",
    "--action",
    type=click.Choice(choices=_actions, case_sensitive=False),
    required=True,
    prompt=False,
    help="Action to take",
    default="dump",
)
def cli_command(input: IOBase, action: str) -> None:
    pngstuff_action(input, Action(action))


def pngstuff_action(input: IOBase, action: Action) -> None:
    match action:
        case Action.DUMP:
            dump(input)


def dump(input: IOBase) -> None:
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
