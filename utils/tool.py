import logging

from utils.currency import currency_dict


def to_datetime(s: str):
    '''
    将yyyymmdd字符串转换成yyyy-mm-dd字符串，包括了对日期合法性的判断
    :param s: yyyymmdd字符串
    :return: yyyy-mm-dd字符串
    '''
    def validate_string(str_to_validate):
        if len(str_to_validate) != 8:
            return False
        if not str_to_validate.isdigit():
            return False
        return True

    def validate_date(year, month, day):
        if year < 0 or month < 1 or month > 12 or day < 1 or day > 31:
            return False
        if month in [4, 6, 9, 11] and day > 30:
            return False
        if month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                if day > 29:
                    return False
            elif day > 28:
                return False
        return True

    if not validate_string(s):
        raise ValueError(f"{s}长度不为8或者不是纯数字！")
    year = int(s[:4])
    month = int(s[4:6])
    day = int(s[6:])
    if not validate_date(year, month, day):
        raise ValueError(f"{s}不是一个合法日期")
    return f"{year}-{month}-{day}"


def get_currency(symbol: str, allow_list=None):
    '''
    将货币符号转换为货币的中文名称（与中国银行官网对应）
    :param symbol: 货币符号
    :param allow_list: 可选的货币名称，如果货币名称没有在中国银行的系统的则报错
    :return:
    '''
    if allow_list is None:
        allow_list = []
    if symbol not in currency_dict:
        raise ValueError(f"{symbol}不是一个合法的货币符号")
    chinese_name = currency_dict.get(symbol)
    for a in allow_list:
        if a not in currency_dict.values():
            logging.warning(f"货币名称 {a} 未知")
    if len(allow_list) > 0:
        if chinese_name not in allow_list:
            raise ValueError(f"系统中没有该货币：{chinese_name}")
    return chinese_name


if __name__ == '__main__':
    '''
    对to_datetime的测试
    '''
    assert to_datetime("20211025") == "2021-10-25"
    assert to_datetime("20240228")
    assert to_datetime("20230227")

    error_date = ["20211801", "20211135", "20240228"]
    for d in error_date:
        try:
            to_datetime("20211801")
        except ValueError:
            pass
        except Exception as e:
            raise e
