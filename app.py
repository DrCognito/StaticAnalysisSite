from os import environ
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path="setup.env")


def get_metadata_files(path: Path) -> dict:
    output = {}
    metadata_paths = path.glob('**/meta_data.json')
    for p in metadata_paths:
        name = str(p.parent).split('\\')[-1]
        output[name] = p

    return output


metadata_dict = get_metadata_files(Path(environ['PLOT_DIRECTORY']))
