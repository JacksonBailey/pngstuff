from abc import ABC, abstractmethod
from enum import Enum
from typing import BinaryIO, Optional
import click


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
def cli_command(input: BinaryIO, output: Optional[BinaryIO], action: str) -> None:
    pngstuff_action(input=input, output=output, action=Action(action))


def pngstuff_action(
    input: BinaryIO, output: Optional[BinaryIO], action: Action
) -> None:
    match action:
        case Action.DUMP:
            walk_file(input=input, consumer=PngDumper())
        case Action.STRIP:
            assert output is not None, "Expected somewhere to send output"
            walk_file(input=input, consumer=PngStripper(output=output))


class PngConsumer(ABC):
    @abstractmethod
    def consumeHeader(self, header: bytes) -> None:
        assert header == b"\x89PNG\r\n\x1a\n", "Improper file header '{header}'"

    @abstractmethod
    def consumeChunk(
        self,
        chunk_length_bytes: bytes,
        chunk_length: int,
        chunk_type: bytes,
        chunk_data: bytes,
        chunk_crc: bytes,
    ) -> None:
        pass


class PngDumper(PngConsumer):
    def consumeHeader(self, header: bytes) -> None:
        super()

    def consumeChunk(
        self,
        chunk_length_bytes: bytes,
        chunk_length: int,
        chunk_type: bytes,
        chunk_data: bytes,
        chunk_crc: bytes,
    ) -> None:
        if chunk_type == b"IDAT":
            click.echo(
                f"{chunk_type}\t{chunk_length}\t(omitted image data)\t{chunk_crc}"
            )
        else:
            click.echo(f"{chunk_type}\t{chunk_length}\t{chunk_data}\t{chunk_crc}")


class PngStripper(PngConsumer):
    def __init__(self, output: BinaryIO):
        self.output = output

    def consumeHeader(self, header: bytes) -> None:
        super()
        self.output.write(header)

    def consumeChunk(
        self,
        chunk_length_bytes: bytes,
        chunk_length: int,
        chunk_type: bytes,
        chunk_data: bytes,
        chunk_crc: bytes,
    ) -> None:
        if chunk_type not in [b"IHDR", b"IDAT"]:
            click.echo(f"{chunk_type}\t{chunk_length}\t{chunk_data}\t{chunk_crc}")
        else:
            self.output.write(chunk_length_bytes)
            self.output.write(chunk_type)
            self.output.write(chunk_data)
            self.output.write(chunk_crc)


def walk_file(input: BinaryIO, consumer: PngConsumer) -> None:
    consumer.consumeHeader(header=input.read(8))
    while True:
        chunk_length_bytes = input.read(4)
        chunk_length = int.from_bytes(chunk_length_bytes, byteorder="big")
        if not chunk_length:
            break
        chunk_type = input.read(4)
        chunk_data = input.read(chunk_length)
        chunk_crc = input.read(4)
        consumer.consumeChunk(
            chunk_length_bytes=chunk_length_bytes,
            chunk_length=chunk_length,
            chunk_type=chunk_type,
            chunk_data=chunk_data,
            chunk_crc=chunk_crc,
        )
