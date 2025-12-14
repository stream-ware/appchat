import argparse
import json

from apps.maps.geocoding_service import MapSearchService


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", default="Warszawa")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    svc = MapSearchService()
    result = svc.search(args.query, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
