import subprocess


def __str_type_checker_and_print_info(data: str) -> None:
    print(f'Содержание переменной: {data}')
    print(f'Тип переменной: {type(data)}')


def __bytes_type_checker_and_print_info(data: bytes) -> None:
    print(f'Содержание переменной: {data}')
    print(f'Тип переменной: {type(data)}')
    print(f'Длина переменной: {len(data)}')


def __encoding_str(data_in_str: str) -> bytes:
    print(f'Данные "{data_in_str}" типа {type(data_in_str)}')
    return data_in_str.encode('utf-8')


def __decoding_bytes(data_in_bytes: bytes) -> str:
    print(f'Данные "{data_in_bytes}" типа {type(data_in_bytes)}')
    return data_in_bytes.decode('utf-8')


def __ping_resource(args) -> None:
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    i: int = 0

    for byte_line in subproc_ping.stdout:
        byte_line = byte_line.decode('cp866').encode('utf-8')
        print(byte_line.decode('utf-8'))
        i += 1
        if i > 4:
            break


if __name__ == '__main__':

    """-----   Задание № 1   -----"""

    word_develop_in_Russian: str = 'разработка'
    word_socket_in_Russian: str = 'сокет'
    word_decorator_in_Russian: str = 'декоратор'

    __str_type_checker_and_print_info(word_develop_in_Russian)
    __str_type_checker_and_print_info(word_socket_in_Russian)
    __str_type_checker_and_print_info(word_decorator_in_Russian)

    word_develop_in_Russian_by_utf: str = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
    word_socket_in_Russian_by_utf: str = '\u0441\u043e\u043a\u0435\u0442'
    word_decorator_in_Russian_by_utf: str = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'

    __str_type_checker_and_print_info(word_develop_in_Russian_by_utf)
    __str_type_checker_and_print_info(word_socket_in_Russian_by_utf)
    __str_type_checker_and_print_info(word_decorator_in_Russian_by_utf)

    """-----   Задание № 2   -----"""

    word_class_in_bytes: bytes = b'class'
    word_function_in_bytes: bytes = b'function'
    word_method_in_bytes: bytes = b'method'

    __bytes_type_checker_and_print_info(word_class_in_bytes)
    __bytes_type_checker_and_print_info(word_function_in_bytes)
    __bytes_type_checker_and_print_info(word_method_in_bytes)

    """-----   Задание № 3   -----"""

    item_1: bytes = b'attribute'
    # item_2: bytes = b'класс'      данная операция вызывает исключение SyntaxError
    # item_3: bytes = b'функция'    данная операция вызывает исключение SyntaxError
    item_4: bytes = b'type'

    """-----   Задание № 4   -----"""

    transformed_str: list = [
        'разработка',
        'администрирование',
        'protocol',
        'standard'
    ]

    for word in transformed_str:
        __decoding_bytes(__encoding_str(word))

    """-----   Задание № 5   -----"""

    yandex_ping: tuple = ('ping', 'yandex.ru')
    youtube_ping: tuple = ('ping', 'youtube.com')

    __ping_resource(yandex_ping)
    __ping_resource(youtube_ping)

    """-----   Задание № 6   -----"""

    strings_for_file: tuple = (
        'сетевое программирование',
        'сокет',
        'декоратор'
    )

    with open(file='test_file.txt', mode='w') as file:
        for line in strings_for_file:
            file.write(f'{line}\n')
        print(file)

    with open(file='test_file.txt', mode='r', encoding='UTF-8') as file:
        for line in file:
            print(line)
