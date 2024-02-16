# 笔试题

@陈方熠

**目录结构**

- [Q1.py](./Q1.py)                   # 第一题程序
- [Q2.py](./Q2.py)                   # 第二题程序
- [result.txt](./result.txt)         # 第一题输出的例子文件
- [requirements.txt](./requirements.txt) # 依赖
- [utils/](./utils)                   # 辅助用，解耦了一些转换函数
  - [tool.py](./utils/tool.py)       # 解耦了一些转换函数
  - [currency.py](./utils/currency.py)   # 一些关键映射表和常量
- [webdriver/](./webdriver)           # webdriver所在驱动目录
- [example/](./webdriver/example)   # 第一题生成的例子

# 第一题

### 依赖版本

```
selenium==4.17.2
```

**低于4.0.0的selenium无法使用该程序。**

### 使用

```shell
python3 Q1.py 20211231 USD
```

```python
'''
Output 636.99
in result.txt:
货币符号, 货币名称, 现汇卖出价, 发布时间
USD, 美元, 636.99, 2021.12.31 23:42:27
'''
```

考虑的因素

*   支持Chrome或者Edge
*   支持爬取多条数据写入result.txt
*   异常捕获
*   对货币符号和日期的检查
*   考虑到当前页面不存在任何可用的现汇卖出价（栏目为空或者没有搜索到数据）的场景

# 第二题

```shell
python3 Q2.py
```

