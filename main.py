import argparse
import requests
from bs4 import BeautifulSoup
from loguru import logger
from config import name_path, data_file_name
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.backends.backend_tkagg as tkagg
from PyQt5 import QtWidgets


def get_soup(url):
    r = requests.get(url, verify=False)
    r.encoding = 'gb2312'
    return BeautifulSoup(r.text, 'lxml')


def get_latest_num():
    """获取最新一期的期数"""
    latest_url = 'http://datachart.500.com/ssq/history/newinc/history.php'
    latest_soup = get_soup(latest_url)
    latest_num = latest_soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]  # 最新的期数
    return int(latest_num)


def run(name):
    latest_num = get_latest_num()  # 最新的期数

    start = 1
    url = f'http://datachart.500.com/{name}/history/newinc/history.php?start={start}&end={latest_num}'

    soup = get_soup(url)
    rows = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")  # 所有行
    print(len(rows))

    dtype = np.dtype([
        ('current_number', 'U10'),
        ('red_ball1', 'U2'),
        ('red_ball2', 'U2'),
        ('red_ball3', 'U2'),
        ('red_ball4', 'U2'),
        ('red_ball5', 'U2'),
        ('red_ball6', 'U2'),
        ('blue_ball', 'U2'),
        ('prize_pool_bonus', np.uint64),
        ('first_prize_number', np.uint64),
        ('first_prize_bonus', np.uint64),
        ('second_prize_number', np.uint64),
        ('second_prize_bonus', np.uint64),
        ('total_amount', np.uint64),
        ('award_date', 'U10')
    ])
    data = np.empty(len(rows), dtype=dtype)  # 创建一个空的结构化数组

    for i in range(len(rows)):
        all_td = rows[i].find_all('td')
        current_number = all_td[0].text  # 当前期数
        red_ball1 = all_td[1].text  # 红球1
        red_ball2 = all_td[2].text  # 红球2
        red_ball3 = all_td[3].text  # 红球3
        red_ball4 = all_td[4].text  # 红球4
        red_ball5 = all_td[5].text  # 红球5
        red_ball6 = all_td[6].text  # 红球6
        blue_ball = all_td[7].text  # 蓝球
        prize_pool_bonus = all_td[9].text.replace(',', '')  # 奖池奖金
        first_prize_number = all_td[10].text.replace(',', '')  # 一等奖注数
        first_prize_bonus = all_td[11].text.replace(',', '')  # 一等奖单注奖金
        second_prize_number = all_td[12].text.replace(',', '')  # 二等奖注数
        second_prize_bonus = all_td[13].text.replace(',', '')  # 二等奖单注奖金
        total_amount = all_td[14].text.replace(',', '')  # 总投注额
        award_date = all_td[15].text  # 开奖日期

        # print(i, current_number, red_ball1, red_ball2, red_ball3, red_ball4, red_ball5, red_ball6, blue_ball, prize_pool_bonus, first_prize_number, first_prize_bonus,
        #       second_prize_number, second_prize_bonus, total_amount, award_date)

        data[i]['current_number'] = current_number
        data[i]['red_ball1'] = red_ball1
        data[i]['red_ball2'] = red_ball2
        data[i]['red_ball3'] = red_ball3
        data[i]['red_ball4'] = red_ball4
        data[i]['red_ball5'] = red_ball5
        data[i]['red_ball6'] = red_ball6
        data[i]['blue_ball'] = blue_ball
        data[i]['prize_pool_bonus'] = prize_pool_bonus
        data[i]['first_prize_number'] = first_prize_number
        data[i]['first_prize_bonus'] = first_prize_bonus
        data[i]['second_prize_number'] = second_prize_number
        data[i]['second_prize_bonus'] = second_prize_bonus
        data[i]['total_amount'] = total_amount
        data[i]['award_date'] = award_date

    # print(data)
    df = pd.DataFrame(data)
    df.to_csv("{}{}".format(name_path[name]["path"], data_file_name), encoding="utf-8")

    # logger.info('【{}】最新一期期号：{}'.format(name_path[name]['name'], current_num))

    draw(df, name, 'prize_pool_bonus', '奖池奖金')
    draw(df, name, 'first_prize_number', '一等奖注数')
    draw(df, name, 'first_prize_bonus', '一等奖单注奖金')
    draw(df, name, 'second_prize_number', '二等奖注数')
    draw(df, name, 'second_prize_bonus', '二等奖单注奖金')
    draw(df, name, 'total_amount', '总投注额')


def draw(df, name, column_name, ylabel):
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig = plt.figure(figsize=(16, 9))
    df_copy = df.copy()
    df_copy['award_date'] = pd.to_datetime(df_copy['award_date'])  # 转换为日期时间类型
    df_copy.set_index('award_date', inplace=True)  # 设置 'award_date' 列为 DataFrame 的索引
    df_filtered = df_copy[df_copy.index.day % 5 == 0]  # 保留开奖日能被 N 整除的行

    min_date = df_filtered.index.min().to_period('Y').start_time
    max_date = df_filtered.index.max().to_period('Y').end_time
    x_ticks = pd.date_range(start=min_date, end=max_date, freq='YS')  # 设置 X 轴的刻度间隔为每隔 1 年
    plt.xticks(x_ticks, x_ticks.strftime('%Y'))  # X轴只显示年份，不显示月、日、时间

    df_filtered.reset_index(inplace=True)  # 重新设置索引，恢复为普通列
    plt.plot(df_filtered['award_date'], df_filtered[column_name], label='Column')

    plt.xlabel('年份')
    plt.ylabel(ylabel)
    plt.title(f'{ylabel}随时间变化')
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    plt.savefig(name_path[name]['analysis'] + column_name + '.png')
    # plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='ssq', type=str, help='选择爬取数据: 双色球/大乐透')
    args = parser.parse_args()

    run(name=args.name)
