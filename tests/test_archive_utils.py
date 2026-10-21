"""Archive extraction must reject traversal and link escapes."""

import io
import stat
import tarfile
import zipfile

import pytest

from superfreetts_addon import archive_utils


@pytest.mark.unit
def test_safe_extract_zip_writes_nested_file(tmp_path):
    archive = tmp_path / "ok.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("nested/hello.txt", "hello")

    destination = tmp_path / "dest"
    archive_utils.safe_extract_zip(archive, destination)

    assert (destination / "nested" / "hello.txt").read_text(encoding="utf-8") == "hello"


@pytest.mark.unit
def test_safe_extract_zip_rejects_traversal(tmp_path):
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../escaped.txt", "owned")

    with pytest.raises(archive_utils.UnsafeArchiveError):
        archive_utils.safe_extract_zip(archive, tmp_path / "dest")
    assert not (tmp_path / "escaped.txt").exists()


@pytest.mark.unit
def test_safe_extract_zip_rejects_absolute_path(tmp_path):
    archive = tmp_path / "evil-abs.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("/tmp/escaped.txt", "owned")

    with pytest.raises(archive_utils.UnsafeArchiveError):
        archive_utils.safe_extract_zip(archive, tmp_path / "dest")


@pytest.mark.unit
def test_safe_extract_zip_rejects_symlink(tmp_path):
    archive = tmp_path / "evil-link.zip"
    info = zipfile.ZipInfo("link")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(info, "target")

    with pytest.raises(archive_utils.UnsafeArchiveError):
        archive_utils.safe_extract_zip(archive, tmp_path / "dest")


@pytest.mark.unit
def test_safe_extract_tar_writes_nested_file(tmp_path):
    archive = tmp_path / "ok.tar.gz"
    data = b"hello"
    info = tarfile.TarInfo("nested/hello.txt")
    info.size = len(data)
    with tarfile.open(archive, "w:gz") as tf:
        tf.addfile(info, io.BytesIO(data))

    destination = tmp_path / "dest"
    archive_utils.safe_extract(archive, destination)

    assert (destination / "nested" / "hello.txt").read_bytes() == data


@pytest.mark.unit
def test_safe_extract_tar_rejects_traversal(tmp_path):
    archive = tmp_path / "evil.tar.gz"
    data = b"owned"
    info = tarfile.TarInfo("../escaped.txt")
    info.size = len(data)
    with tarfile.open(archive, "w:gz") as tf:
        tf.addfile(info, io.BytesIO(data))

    with pytest.raises(archive_utils.UnsafeArchiveError):
        archive_utils.safe_extract(archive, tmp_path / "dest")
    assert not (tmp_path / "escaped.txt").exists()


@pytest.mark.unit
def test_safe_extract_tar_rejects_symlink(tmp_path):
    archive = tmp_path / "evil-link.tar.gz"
    info = tarfile.TarInfo("link")
    info.type = tarfile.SYMTYPE
    info.linkname = "../../outside"
    with tarfile.open(archive, "w:gz") as tf:
        tf.addfile(info)

    with pytest.raises(archive_utils.UnsafeArchiveError):
        archive_utils.safe_extract(archive, tmp_path / "dest")
