import argparse
from pathlib import Path

from app.services.ingestion_service import IngestionService


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest policy documents from a directory")
    parser.add_argument("path", type=Path)
    parser.add_argument("--policy-type", default="general")
    args = parser.parse_args()

    service = IngestionService()
    paths = [args.path] if args.path.is_file() else [path for path in args.path.rglob("*") if path.is_file()]
    for path in paths:
        try:
            result = service.ingest_path(path, args.policy_type)
            print(f"ingested {path}: {result.chunks_created} chunks")
        except Exception as exc:
            print(f"skipped {path}: {exc}")


if __name__ == "__main__":
    main()
