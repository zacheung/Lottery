import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', default='ssq', type=str, help='选择爬取数据: 双色球/大乐透')
    args = parser.parse_args()
