# Attach Metadata to an Instagram Archive (macOS)

Instagram lets users request and download a full archive of their
data, including the images and videos themselves (sans metadata)
and a JSON metadata collection. In particular the JSON file
contains captions (ASCII, so emoji and other UTF-8 characters are
mangled), timestamps, and (if attached) GPS coordinates.

This script/command-line utility batch processes an entire
Instagram archive using [exiftool][] and [SetFile][]. The first
piece should work on any system with `exiftool` installed, but I
think SetFile is an OS X command.

## Dependencies

- macOS
- [exiftool][]

- [Python 3.9+][]
- [click][]
- [pytz][]
- [tqdm][]

## Usage

```
$ python insta-archive-metadata.py --help
Usage: insta-archive-metadata.py [OPTIONS]

Options:
  -s, --source DIRECTORY  Instagram archive root.  [required]
  -o, --output DIRECTORY  Export directory.  [required]
  --help                  Show this message and exit.
```

The command creates a new directory `<Export
Dir>/YYYYMMDD_HHMMSS` for the final, tagged images.

[exiftool]: https://exiftool.org

[Python 3.9+]: https://www.python.org/dev/peps/pep-0585/
[click]: https://click.palletsprojects.com/en/8.0.x/
[pytz]: http://pytz.sourceforge.net
[tqdm]: https://tqdm.github.io
[SetFile]: https://apple.stackexchange.com/a/99599
