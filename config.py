# 数据文件名
data_file_name = 'data.csv'

# 训练列
train_columns = ['red_ball1', 'red_ball2', 'red_ball3', 'red_ball4', 'red_ball5', 'red_ball6', 'blue_ball']

# 路径配置
name_path = {
    'ssq': {
        'name': '双色球',
        'path': 'data/ssq/',
        'analysis': 'analysis/ssq/',
        'log_file': 'log/ssq_log_file.log'
    },
    'dlt': {
        'name': '大乐透',
        'path': 'data/dlt/',
        'analysis': 'analysis/dlt/',
        'log_file': 'log/dlt_log_file.log'
    }
}

model_args = {
    'ssq': {
        'model_args': {
            'windows_size': 3
        }
    }
}
