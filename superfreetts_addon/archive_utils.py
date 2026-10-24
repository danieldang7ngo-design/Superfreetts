"""Safe archive extraction helpers.

Installer archives are downloaded from the network, so they must never be
allowed to write outside their dedicated engine directory.  Python's
``extractall`` does not protect against ``../`` paths or symlink escapes on
Python 3.9, which is why every installer uses these helpers instead.
"""

from __future__ import annotations

import stat
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import Iterable


class UnsafeArchiveError(ValueError):
    """Raised when an archive member could escape the extraction directory."""


MAX_ARCHIVE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GiB
MAX_ARCHIVE_MEMBERS = 200_000


def _safe_target(destination: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    if not normalized or normalized in (".", ".."):
        raise UnsafeArchiveError(f"invalid archive member name: {member_name!r}")
    if normalized.startswith("/"):
        raise UnsafeArchiveError(f"absolute archive path: {member_name!r}")
    if len(normalized) > 1 and normalized[1] == ":":
        raise UnsafeArchiveError(f"drive-qualified archive path: {member_name!r}")

    parts = []
    for part in PurePosixPath(normalized).parts:
        if part in ("", "."):
            continue
        if part == "..":
            raise UnsafeArchiveError(f"path traversal in archive: {member_name!r}")
        parts.append(part)
    if not parts:
        raise UnsafeArchiveError(f"empty archive member name: {member_name!r}")

    destination_resolved = destination.resolve()
    target = destination.joinpath(*parts)
    target_resolved = target.resolve()
    try:
        target_resolved.relative_to(destination_resolved)
    except ValueError as exc:
        raise UnsafeArchiveError(
            f"archive member escapes destination: {member_name!r}"
        ) from exc
    return target


def _check_members(members: Iterable[tuple[str, int]]) -> None:
    total = 0
    count = 0
    for _name, size in members:
        count += 1
        if count > MAX_ARCHIVE_MEMBERS:
            raise UnsafeArchiveError("archive contains too many members")
        total += max(0, size)
        if total > MAX_ARCHIVE_BYTES:
            raise UnsafeArchiveError("archive expands beyond the size limit")


def safe_extract_zip(archive_path, destination) -> None:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive_path, "r") as archive:
        infos = archive.infolist()
        _check_members((info.filename, info.file_size) for info in infos)
        for info in infos:
            if info.flag_bits & 0x1:
                raise UnsafeArchiveError(
                    f"encrypted archive member is not supported: {info.filename!r}"
                )
            mode = (info.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise UnsafeArchiveError(
                    f"symlink in archive is not supported: {info.filename!r}"
                )
            target = _safe_target(destination, info.filename)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info, "r") as source, open(target, "wb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)


def safe_extract_tar(archive_path, destination) -> None:
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:*") as archive:
        members = archive.getmembers()
        _check_members((member.name, member.size) for member in members)
        for member in members:
            if member.issym() or member.islnk():
                raise UnsafeArchiveError(
                    f"links in archive are not supported: {member.name!r}"
                )
            if member.ischr() or member.isblk() or member.isfifo() or member.isdev():
                raise UnsafeArchiveError(
                    f"device in archive is not supported: {member.name!r}"
                )
            target = _safe_target(destination, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise UnsafeArchiveError(
                    f"unsupported archive member type: {member.name!r}"
                )
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise UnsafeArchiveError(
                    f"could not read archive member: {member.name!r}"
                )
            with source, open(target, "wb") as output:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            if member.mode & 0o111:
                target.chmod(member.mode & 0o777)


def safe_extract(archive_path, destination, *, archive_type: str | None = None) -> None:
    archive_path = Path(archive_path)
    if archive_type is None:
        name = archive_path.name.lower()
        if name.endswith(".zip"):
            archive_type = "zip"
        elif name.endswith((".tar.gz", ".tgz", ".tar")):
            archive_type = "tar"
        else:
            raise UnsafeArchiveError(f"unsupported archive type: {archive_path.name}")

    if archive_type == "zip":
        safe_extract_zip(archive_path, destination)
    elif archive_type == "tar":
        safe_extract_tar(archive_path, destination)
    else:
        raise UnsafeArchiveError(f"unsupported archive type: {archive_type}")
