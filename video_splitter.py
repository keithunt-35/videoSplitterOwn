#!/usr/bin/env python3
"""Split a video into smaller segments using FFmpeg."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


TIME_PATTERN = re.compile(r"^(?:(\d+):)?([0-5]?\d):([0-5]?\d(?:\.\d+)?)$")


def parse_duration(value: str) -> float:
    """Return a positive duration in seconds from seconds or HH:MM:SS input."""
    try:
        seconds = float(value)
    except ValueError:
        match = TIME_PATTERN.fullmatch(value)
        if not match:
            raise argparse.ArgumentTypeError(
                "duration must be seconds or HH:MM:SS (for example, 300 or 00:05:00)"
            )
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2))
        seconds = hours * 3600 + minutes * 60 + float(match.group(3))

    if seconds <= 0:
        raise argparse.ArgumentTypeError("duration must be greater than zero")
    return seconds


def build_command(
    input_file: Path, output_pattern: Path, duration: float, reencode: bool
) -> list[str]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(input_file),
        "-map",
        "0",
        "-f",
        "segment",
        "-segment_time",
        str(duration),
        "-segment_start_number",
        "1",
        "-reset_timestamps",
        "1",
        "-avoid_negative_ts",
        "make_zero",
    ]

    if reencode:
        command.extend(["-c:v", "libx264", "-c:a", "aac"])
    else:
        command.extend(["-c", "copy"])

    command.append(str(output_pattern))
    return command


def split_video(
    input_file: Path, output_folder: Path, duration: float, reencode: bool
) -> None:
    if shutil.which("ffmpeg") is None:
        raise RuntimeError(
            "FFmpeg is required but was not found. Install it with "
            "`brew install ffmpeg` and try again."
        )

    if not input_file.is_file():
        raise FileNotFoundError(f"input video does not exist: {input_file}")

    output_folder.mkdir(parents=True, exist_ok=True)
    extension = input_file.suffix or ".mp4"
    output_pattern = output_folder / f"{input_file.stem}_part_%03d{extension}"
    command = build_command(input_file, output_pattern, duration, reencode)

    print(f"Splitting {input_file} into {output_folder}...")
    subprocess.run(command, check=True)
    print("Done.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Split a large video into smaller files of a specified duration."
    )
    parser.add_argument("input", type=Path, help="path to the input video")
    parser.add_argument(
        "duration",
        type=parse_duration,
        help="segment length in seconds or HH:MM:SS, e.g. 300 or 00:05:00",
    )
    parser.add_argument(
        "output_folder", type=Path, help="folder where the smaller videos are saved"
    )
    parser.add_argument(
        "--reencode",
        action="store_true",
        help="re-encode for more exact cut points; slower than stream copying",
    )
    args = parser.parse_args()

    try:
        split_video(args.input, args.output_folder, args.duration, args.reencode)
    except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())