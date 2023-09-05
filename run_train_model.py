import argparse
import os
import sys
from loguru import logger
import pandas as pd
import numpy as np
from config import name_path, data_file_name, train_columns, model_args


def write_log(message, level='INFO'):
    """
    日志记录，INFO级别记录到文件，ERROR级别记录到文件并退出程序
    """
    if level == 'INFO':
        logger.add(name_path[args.name]['log_file'], level="INFO")
        logger.info(message)
    elif level == 'ERROR':
        logger.add(name_path[args.name]['log_file'], level="ERROR")
        logger.error(message)
        sys.exit()


def create_data(name, windows_size, data):
    """
    创建字典数据集，把数据集切分为一个个的windows_size+1行数据，第一行为y_data，第二行到最后一行为x_data
    """
    data = data.values  # 转换为numpy数组
    write_log(f'当前数据子集shape:{data.shape}')
    x_data, y_data = [], []
    for i in range(len(data) - windows_size):
        sub_data = data[i:(i + windows_size + 1), :]  # 取windows_size+1行数据
        y_data.append(sub_data[0])  # 取第一行数据
        x_data.append(sub_data[1:])  # 取第二行到最后一行数据

    cut_num = 6 if name == "ssq" else 5  # 双色球6个红球，大乐透5个红球
    x_data = np.array(x_data)
    y_data = np.array(y_data)

    # print(x_data.shape)
    # print(y_data.shape)
    # 把红球和蓝球分开，因为红球和蓝球的数值范围是不一样的，红球和蓝球有可能存在相同的数字
    data_dic = {
        "red": {
            "x_data": x_data[:, :, :cut_num], "y_data": y_data[:, :cut_num]
        },
        "blue": {
            "x_data": x_data[:, :, cut_num:], "y_data": y_data[:, cut_num:]
        }
    }
    return data_dic


def train_red_ball_model(name, x_train, y_train, x_test, y_test):

    pass


def run(name, train_test_ratio):
    if train_test_ratio < 0.6:
        write_log("训练集占比不能小于0.6", level='ERROR')
    else:
        write_log(f'训练集占比{train_test_ratio}，开始切分数据集')

    path = name_path[name]['path'] + data_file_name  # 数据集文件路径
    if not os.path.exists(path):
        write_log(f'数据文件不存在，请先执行 get_data.py 脚本爬取数据', level='ERROR')

    data = pd.read_csv(path)
    write_log(f'原始数据集shape:{data.shape}')
    windows_size = model_args[name]['model_args']['windows_size']
    train_d = create_data(name, windows_size, data.iloc[:int(len(data) * train_test_ratio)].loc[:, train_columns])  # 取前train_test_ratio比例的数据作为训练集
    test_d = create_data(name, windows_size, data.iloc[int(len(data) * train_test_ratio):].loc[:, train_columns])  # 取后1-train_test_ratio比例的数据作为测试集

    train_red_ball_model(name, train_d["red"]["x_data"], train_d["red"]["y_data"], test_d["red"]["x_data"], test_d["red"]["y_data"])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='ssq', type=str, help='选择爬取数据: 双色球/大乐透')
    parser.add_argument('--train_test_ratio', default=0.7, type=float, help="训练集占比，设置大于等于0.6")
    args = parser.parse_args()

    run(name=args.name, train_test_ratio=args.train_test_ratio)
