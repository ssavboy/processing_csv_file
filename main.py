#!/path/to/folder/python_interpreter/venv/bin/python3

import argparse
import csv
import sys

from tabulate import tabulate


def setup_arg_parser():
    """Настройка и создание парсера аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Обработчик CSV-файлов')
    parser.add_argument('file', help='Путь к CSV-файлу')
    parser.add_argument(
        '--where',
        help='Условие фильтрации в формате "колонка>значение" или "колонка=значение"')
    parser.add_argument('--aggregate',
                        help='Агрегация в формате "колонка=операция" (avg, min, max)')
    return parser


def load_data(file_path):
    """Загрузка данных из CSV файла"""
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.", file=sys.stderr)
        sys.exit(1)


def parse_condition(condition_str):
    """Парсинг условия фильтрации"""
    operators = ['>=', '<=', '>', '<', '=']
    for op in operators:
        if op in condition_str:
            col, val = condition_str.split(op)
            return col.strip(), op, val.strip()
    print("Ошибка: Неверный формат условия фильтрации", file=sys.stderr)
    sys.exit(1)


def apply_filter(data, condition_str):
    """Применение фильтра к данным"""
    if not condition_str:
        return data

    col, op, val = parse_condition(condition_str)
    filtered_data = []

    for row in data:
        try:
            # Проверка условия равенства для строк и чисел
            if op == '=':
                if row[col] == val:
                    filtered_data.append(row)
            # Проверка условий только для чисел
            else:
                if float(row[col]) > float(val) and op == '>':
                    filtered_data.append(row)
                elif float(row[col]) < float(val) and op == '<':
                    filtered_data.append(row)
                elif float(row[col]) >= float(val) and op == '>=':
                    filtered_data.append(row)
                elif float(row[col]) <= float(val) and op == '<=':
                    filtered_data.append(row)
        # Если колонка не существует или же преобразование в число не возможно
        except (KeyError, ValueError) as e:
            print(f"Ошибка при фильтрации: {e}", file=sys.stderr)
            sys.exit(1)

    return filtered_data


def parse_aggregation(aggregate_str):
    """Парсинг условия агрегации"""
    if '=' not in aggregate_str:
        print("Ошибка: Неверный формат агрегации", file=sys.stderr)
        sys.exit(1)
    col, agg_func = aggregate_str.split('=')
    return col.strip(), agg_func.strip().lower()


def calculate_aggregation(data, aggregate_str):
    """Вычисление агрегации"""
    if not aggregate_str:
        return None

    col, agg_func = parse_aggregation(aggregate_str)

    try:
        values = [float(row[col]) for row in data if row[col]]
        if not values:
            return None

        if agg_func == 'avg':
            return sum(values) / len(values)
        elif agg_func == 'min':
            return min(values)
        elif agg_func == 'max':
            return max(values)
        else:
            print(f"Ошибка: Неподдерживаемая операция агрегации '{agg_func}'", file=sys.stderr)
            sys.exit(1)
    except (KeyError, ValueError) as e:
        print(f"Ошибка при агрегации: {e}", file=sys.stderr)
        sys.exit(1)


def display_results(data, aggregation_result, aggregte_str=None):
    """Вывод результатов"""
    if aggregation_result is not None and aggregte_str:
        col, agg_func = parse_aggregation(aggregte_str)
        print(f"\nРезультат агрегации {agg_func}({col}): {aggregation_result:.2f}\n")
    else:
        if data:
            print("\nРезультаты фильтрации:")
            print(tabulate(data, headers="keys", tablefmt="grid"))
        else:
            print("\nНет данных, соответствующих условиям фильтрации")


def main():
    """Основная функция"""
    parser = setup_arg_parser()
    args = parser.parse_args()

    data = load_data(args.file)
    filtered_data = apply_filter(data, args.where)
    aggregation_result = calculate_aggregation(filtered_data, args.aggregate)
    display_results(filtered_data, aggregation_result, args.aggregate)


if __name__ == '__main__':
    main()
