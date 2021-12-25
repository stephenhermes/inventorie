from pathlib import Path
from reader import JamecoInventoryReader, TaydaInventoryReader

if __name__ == '__main__':

    pdf_file = Path(__file__).resolve().parents[2] / 'example' / 'Jameco.pdf'
    jameco_reader = JamecoInventoryReader()
    df = jameco_reader.read(pdf_file)
    
    print('::: Jameco :::')
    print(df.head())

    email_file = Path(__file__).resolve().parents[2] / 'example' / 'Tayda.eml'
    tayda_reader = TaydaInventoryReader()
    df = tayda_reader.read(email_file)
    
    print('\n::: Tayda :::')
    print(df.head())
