# Evaluate how well the generated graphs match the given probability

import random
import networkx as nx
import numpy as np
import csv

class SBMEvaluator(object):
    '''
    Function:
        Given the .csv files of SBMGraph, calculate the sampled frequency of edges,
        bith in_block and cross_block.
    Args:
        community_size: size distribution of the SBM Graph
        inblock_prob: ideal inblock prob.
        crossblock_prob: ideal crossblock prob.
    '''

    def __init__(self, community_size=None, inblock_prob=0.2, crossblock_prob=0.01, adj_file=None, cmt_file=None):
        assert community_size is not None
        self._community_size = community_size
        self._inblock_prob = inblock_prob
        self._crossblock_prob = crossblock_prob
        self._adj_file = adj_file
        self._cmt_file = cmt_file

        self._node_num = sum(self._community_size)
        self.build_cmt_dict()
        self.measure()

    def build_cmt_dict(self):
        # |node_id |cmt_id |
        col_types = [int, int]
        with open(self._cmt_file) as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            node_cmt_list = []
            for row in f_csv:
                row = tuple(convert(value) for convert, value in zip(col_types, row))
                node_cmt_list.append(row)
        self.cmt_dict = dict(node_cmt_list)

    def measure(self):
        edge_max_num = self._node_num * (self._node_num-1) # undirected graph
        self.inblock_max_num = 0
        for _, size in enumerate(self._community_size):
            self.inblock_max_num += size * (size-1)
        
        self.crossblock_max_num = edge_max_num - self.inblock_max_num
        
        self.inblock_num = 0
        self.crossblock_num = 0
        # |source |target |weight |
        col_types = [int, int, int]
        with open(self._adj_file) as f:
            f_csv = csv.reader(f)
            headers = next(f_csv)
            # traverse the edges
            for row in f_csv:
                row = tuple(convert(value) for convert, value in zip(col_types, row))
                if self.cmt_dict[row[0]] == self.cmt_dict[row[1]]:
                    self.inblock_num += 1
                elif self.cmt_dict[row[0]] != self.cmt_dict[row[1]]:
                    self.crossblock_num += 1

        self.inblock_freq = self.inblock_num / self.inblock_max_num
        self.crossblock_freq = self.crossblock_num / self.crossblock_max_num

    def report(self):
        print('The community size of SBM Graph is '+str(self._community_size))
        print('The Ideal inblock prob. is %.4f' % self._inblock_prob)
        print('The Generated inblock freq. is %.4f' % self.inblock_freq)
        print('The Ideal crossblock prob. is %.4f' % self._crossblock_prob)
        print('The Generated crossblock freq. is %.4f' % self.crossblock_freq)

if __name__ == '__main__':
    my_Evaluator = SBMEvaluator(community_size=[500, 500], inblock_prob=0.2,
                     crossblock_prob=0.05, adj_file='./sbm_1000n_adj.csv', cmt_file='./sbm_1000n_cmt.csv')
    my_Evaluator.report()
