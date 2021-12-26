from pathlib import Path

from supplier import get_reader_from_file

if __name__ == '__main__':

    workdir = Path(__file__).resolve().parents[2] / 'example'
    for file in workdir.glob('*'):
        reader = get_reader_from_file(file)
        df = reader.read(file)
        print('\n:::', reader.__class__.__name__, ':::')
        print(df)
