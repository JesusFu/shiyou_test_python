'''
@陈方熠
'''
import argparse
import logging
import os.path
from time import sleep

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService

from utils.currency import heads, default_head
from utils.tool import to_datetime, get_currency


class ExchangeRateGetter:
    def __init__(self):
        '''
        可以根据系统环境使用Edge或者Chrome
        '''

        def _use_edge():
            self.options = webdriver.EdgeOptions()
            self.options.add_argument('--headless')
            self.service = EdgeService(executable_path="webdriver/edge/msedgedriver.exe")
            self.driver = webdriver.Edge(service=self.service, options=self.options)

        def _use_chrome():
            self.options = webdriver.ChromeOptions()
            self.options.add_argument('--headless')
            self.service = ChromeService(executable_path="webdriver/chrome/chromedriver.exe")
            self.driver = webdriver.Chrome(service=self.service, options=self.options)

        browsers = [_use_chrome, _use_edge]

        for b in browsers:
            try:
                b()
                return
            except WebDriverException as e:
                continue

        self.driver = None
        raise EnvironmentError(f"创建driver失败")

    def _set_datetime(self, date):
        '''
        用于设置页面中搜索框的日期
        :param date: 格式化的日期字符串
        :return: 无
        '''
        start_time = self.driver.find_element(By.NAME, "erectDate")
        start_time.send_keys(date)

        end_time = self.driver.find_element(By.NAME, "nothing")
        end_time.send_keys(date)

    def _set_currency_type(self, currency):
        '''
        由于设置货币框的货币类型
        :param currency: 货币符号
        :return: 无
        '''
        exchange = self.driver.find_element(By.NAME, "pjname")
        select = Select(exchange)
        options = [str(option.get_attribute("value")) for option in select.options][1:]
        # 读取货币框的下拉菜单，以一种比较鲁棒的方法判断用户输入的货币是否合法。
        select.select_by_value(get_currency(currency, options))

    def _set_search_button(self):
        '''
        点击搜索按钮
        :return: 无
        '''
        search_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="historysearchform"]/div/table/tbody/tr/td[7]/input'))
        )
        # 根据XPATH找到按钮。
        search_button.click()
        sleep(1)

    def _get_table_info(self, count=1):
        '''
        获取表格中的信息
        :param count: 需要存入文件的数据数量，-1为全部存储，默认为1
        :return: 现汇卖出价以及那一行的其他信息
        '''
        allowed = default_head

        def _handle_single_table():
            table_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'BOC_main'))
            ) # 使用wait来应对那些网络不好没有刷新出页面的场景

            rows = table_element.find_elements(By.TAG_NAME, 'tr')

            res = []

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')

                row_content = []
                for cell in cells:
                    row_content.append(cell.text)
                result = dict(zip(heads, row_content))
                res.append({k: str(result.get(k, '')) for k in allowed if k in heads})

            return res

        '''
        一种可能的情况是，当前页面不存在任何可用的现汇卖出价(比如新台币)。
        此时就需要一直点击下一页，直到找到一个可用的现汇卖出价
        如果一个都没有，或者没有返回结果（通常是当前日期没有数据），直接报错，提示没有可用的现汇卖出价
        '''

        try:
            page_info = self.driver.find_element(By.CSS_SELECTOR, '#list_navigator > ol > li:nth-child(1)')
            max_page = int(page_info.text[1:-1])
        except:
            max_page = 0

        # max_page是分页器左侧“共X页”中显示的最大页面数
        if max_page <= 0:
            raise ValueError("当前日期和货币没有找到任何现汇卖出价！")

        return_datas = []

        page = 1
        while (page <= max_page):
            single_table_res = _handle_single_table()
            for r in single_table_res:
                if r.get('现汇卖出价') != '':
                    return_datas.append(r)
                if len(return_datas) >= count > 0:
                    break
            if len(return_datas) >= count > 0:
                break
            page = page + 1
            next_page = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'body > div > div.BOC_main > div.pb_ft.clearfix > div > ol > li.turn_next > a'))
            )
            next_page.click()

        if len(return_datas) >= 1:
            return return_datas[0].get("现汇卖出价"), return_datas

        raise ValueError("当前日期和货币没有找到任何现汇卖出价！")

    def _write_into_text(self, symbol, datas):
        '''
        写入txt
        :param symbol:货币符号
        :param data:需要写入的数据
        :return:
        '''
        if not os.path.exists(f"result.txt"):
            with open('result.txt', 'w', encoding='utf8') as f:
                f.write(", ".join(['货币符号'] + default_head) + "\n")

        with open('result.txt', 'a', encoding='utf8') as f:
            for data in datas:
                f.write(", ".join([symbol] + list(data.values())) + "\n")

    def get_currency(self, date, currency, count=1):
        try:
            # 标准化日期字符串
            date_formatted = to_datetime(date)

            self.driver.get('https://www.boc.cn/sourcedb/whpj/')

            self._set_datetime(date_formatted)
            self._set_currency_type(currency)
            self._set_search_button()
            display, datas = self._get_table_info(count=count)
            self._write_into_text(currency, datas)
            return display
        except Exception as e:
            logging.error(f"发生错误: {e}")
        finally:
            self.driver.quit()


def parse_arguments():
    parser = argparse.ArgumentParser(description='外汇牌价查询.')

    parser.add_argument('date', type=str, help='查询的日期')
    parser.add_argument('currency', type=str, help='查询的货币符号')
    parser.add_argument('--count', type=int, default=1, help='输出到文件的数据量，默认为1，-1为全部。', required=False)

    args = parser.parse_args()

    erg = ExchangeRateGetter()
    exchange_rate = erg.get_currency(args.date, args.currency, args.count)
    if exchange_rate:
        print(exchange_rate)


if __name__ == "__main__":
    parse_arguments()
