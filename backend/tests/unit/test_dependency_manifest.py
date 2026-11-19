from pathlib import Path


def test_starlette_session_signing_dependency_is_declared() -> None:
    requirements = Path(__file__).parents[2] / "requirements.txt"
    packages = {
        line.strip().split("==", 1)[0].lower()
        for line in requirements.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert "itsdangerous" in packages
