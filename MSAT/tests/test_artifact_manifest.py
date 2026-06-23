from inference.artifact_manifest import file_manifest


def test_file_manifest_records_stable_fingerprint(tmp_path):
    ckpt = tmp_path / 'model.pt'
    ckpt.write_bytes(b'checkpoint-bytes')

    manifest = file_manifest(ckpt)

    assert manifest['exists'] is True
    assert manifest['path'] == str(ckpt.resolve())
    assert manifest['size_bytes'] == len(b'checkpoint-bytes')
    assert manifest['sha256'] == (
        '68ff0e8c172a352fc955978d2357b69ca36d9836'
        'f5a251bdcafe408960449e8d'
    )


def test_file_manifest_marks_missing_file(tmp_path):
    missing = tmp_path / 'missing.pt'

    manifest = file_manifest(missing)

    assert manifest == {
        'path': str(missing.resolve()),
        'exists': False,
    }
