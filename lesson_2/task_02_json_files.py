import json
import re
from datetime import datetime

from task_01_csv_files import get_files_names, TD

JSON_FILE_TYPE = re.compile(r'^\w*(\d*.json)$')


def write_order_to_json(item: str = None,
                        quantity: int = None,
                        price: float = None,
                        buyer: str = None,
                        date: str = str(datetime.now())) -> None:

    file_name = next(get_files_names(TD, JSON_FILE_TYPE))
    if all([item,
            quantity,
            price,
            buyer,
            date]):

        order = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }

        with open(f'{TD}/{file_name}', 'r') as f:
            orders = json.load(f)

        with open(f'{TD}/{file_name}', 'w') as f:
            orders['orders'].append(order)
            json.dump(orders, f, sort_keys=True, indent=4)

    return


if __name__ == '__main__':
    write_order_to_json(item='Носки', quantity=1, price=10.0, buyer='Петр')
