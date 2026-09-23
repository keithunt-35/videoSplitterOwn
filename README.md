# Video Splitter

Split a large video into smaller files with a chosen duration using Python and
FFmpeg. The input video is not loaded into memory, so this works for large
files.

## Requirements

Install FFmpeg:

```bash
brew install ffmpeg
```

Python 3.9 or newer is recommended.

## Usage

```bash
python3 video_splitter.py input.mp4 300 output_segments
```

The command above creates five-minute files such as
`output_segments/input_part_001.mp4`.

You can also specify the duration as hours, minutes, and seconds:

```bash
python3 video_splitter.py input.mp4 00:05:00 output_segments
```

By default, the video and audio streams are copied without re-encoding. This
is fast and keeps the original quality, but cuts may fall on the nearest video
keyframe. Use `--reencode` when exact cut times matter:

```bash
python3 video_splitter.py input.mp4 00:05:00 output_segments --reencode
```
