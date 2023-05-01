
import yaml

from task_01_csv_files import TD

DATA_FOR_YAML = {
    'list_params': ['param_01', 'param_02'],
    'int_params': 1,
    'dict_params': {
        '\u060B': 2,
        '\u20AB': 3
    }
}

with open(f'{TD}/data_write.yaml', 'w') as f:
    yaml.dump(DATA_FOR_YAML, f, default_flow_style=False, allow_unicode=True)
with open(f'{TD}/data_write.yaml') as f:
    few_data = yaml.load(f, Loader=yaml.SafeLoader)
    if DATA_FOR_YAML == few_data:
        print('OK')
