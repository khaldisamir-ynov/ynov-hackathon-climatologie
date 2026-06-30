from __future__ import annotations

from pathlib import Path

import pandas as pd


def get_csv_files(folder: Path) -> list[Path]:
    return sorted([path for path in folder.glob('*.csv') if path.is_file()])


def concatenate_csv_files(csv_files: list[Path], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data_frames = []
    count = 0
    for csv_file in csv_files:
        count += 1
        print(f'Processing file {count}/{len(csv_files)}: {csv_file}')
        df = pd.read_csv(csv_file, sep=';', encoding='utf-8')
        data_frames.append(df)

    if not data_frames:
        raise FileNotFoundError(f'No CSV files found in {csv_files}')

    combined = pd.concat(data_frames, ignore_index=True, sort=False)
    combined.to_csv(output_file, sep=';', index=False, encoding='utf-8')


if __name__ == '__main__':
    script_dir = Path(__file__).resolve().parent
    csv_folder = script_dir
    csv_files = get_csv_files(csv_folder)
    if not csv_files:
        raise FileNotFoundError(f'No CSV files found in {csv_folder}')

    repo_root = script_dir.parents[1]
    output_file = repo_root / 'data' / 'raw' / 'raw.csv'

    concatenate_csv_files(csv_files, output_file)
    print(f'Wrote concatenated CSV to {output_file}')
