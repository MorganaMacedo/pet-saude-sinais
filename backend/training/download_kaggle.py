import argparse
import json
from pathlib import Path

import kagglehub


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("--output", default="datasets")
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()
    output = Path(arguments.output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    path = kagglehub.dataset_download(arguments.dataset, output_dir=str(output), force_download=arguments.force)
    print(json.dumps({"dataset": arguments.dataset, "path": str(path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
