import csv
import os
import re
from typing import Generator, Optional

TD = './Homework_files'
TXT_FILE_TYPE = re.compile(r'^\w*(\d+.txt)$')
OS_NAME_RE = re.compile(r'Название ОС:\s+[\wА-Яа-я ]+[\wА-Яа-я]')
OS_PROD_RE = re.compile(r'Изготовитель системы:\s+[\wА-Яа-я ]+[\wА-Яа-я]')
OS_CODE_RE = re.compile(r'Код продукта:\s+[\w\-]+')
OS_TYPE_RE = re.compile(r'Тип системы:\s+x\d{2}-\w+')


def write_to_csv(file_name: str) -> None:
    input_data = get_data()

    with open(file=f'{TD}/{file_name}', mode="w") as file:
        csv_file_writer = csv.writer(file)
        csv_file_writer.writerow(input_data[0])
        for i in range(len(input_data) - 2):
            row: list = []
            for j in range(len(input_data[0])):
                row.append(input_data[j + 1][i])
            csv_file_writer.writerow(row)


def get_data() -> list:
    os_prod_list: list = []
    os_name_list: list = []
    os_code_list: list = []
    os_type_list: list = []
    main_data: list = [['Изготовитель системы',
                        'Название ОС', 'Код продукта', 'Тип системы'], ]

    txt_files = get_files_names(TD, TXT_FILE_TYPE)
    for file in txt_files:
        with open(f'{TD}/{file}', 'r', encoding='cp1251') as f:
            for line in f:
                os_name = pars_data(OS_NAME_RE, line)
                if os_name:
                    os_name_list.append(os_name)
                    continue

                os_prod = pars_data(OS_PROD_RE, line)
                if os_prod:
                    os_prod_list.append(os_prod)
                    continue

                os_code = pars_data(OS_CODE_RE, line)
                if os_code:
                    os_code_list.append(os_code)
                    continue

                os_type = pars_data(OS_TYPE_RE, line)
                if os_type:
                    os_type_list.append(os_type)
                    continue

    main_data.append(os_prod_list)
    main_data.append(os_name_list)
    main_data.append(os_code_list)
    main_data.append(os_type_list)

    return main_data


def get_files_names(target_directory: str = None, file_type: re = None) -> Generator:
    output_txt_files_generator = (
        txt_file for txt_file in os.listdir(path=f'{target_directory}')
        if file_type.fullmatch(txt_file)
    )
    return output_txt_files_generator


def pars_data(parser: re, parsing_string: str) -> Optional[str]:
    parsed_line = parser.findall(parsing_string)
    if parsed_line:
        parsed_list = re.split(r"\s{2,}", f'{parsed_line[0]}')
        return parsed_list[1]
    return None


if __name__ == "__main__":
    output_file_name = input('Please? input the output file name: ')
    write_to_csv(f'{output_file_name}.csv')
