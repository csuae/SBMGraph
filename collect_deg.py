import csv
import numpy as np
import matplotlib.pyplot as plt

from collections import Counter


def get_out_deg(filename, header=None):
    '''
    Args:
        filename: .csv file to be processed. The first column should be src nodes.
    Return:
        A collections.Counter() object
    '''
    words_box = []

    with open(filename) as f:
        f_csv = csv.reader(f)
        if header is not None:
            headers = next(f_csv)

        for row in f_csv:
            words_box.extend(row[0].strip().split())

    return Counter(words_box)


def draw_and_save(cnt_dict, filename):
    labels, values = zip(*cnt_dict.items())

    indices = list(int(val) for val in labels)
    plt.figure(figsize=(24,16)) # set img size
    plt.bar(indices, values, 1)

    plt.xticks(indices[::50]) # show x axis
    img_name = filename + '_deg.png'

    plt.savefig(img_name)


if __name__ == '__main__':
    # csv_file = './dataset/youtube/2-edges.csv'
    csv_file = './dataset/dyn_sbm/sbm_1000n_adj_t0.csv'

    out_deg = get_out_deg(csv_file, header=True)
    draw_and_save(out_deg, csv_file)