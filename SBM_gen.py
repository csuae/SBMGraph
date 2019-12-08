# Forked from palash1992/DynamicGEM

import random
import networkx as nx
import numpy as np
import csv


class SBMGraph(object):
    '''
    Function:
        Generate static SBM Graph Model, save as 2 .csv files
        File_1: sbm_<# of nodes>n_adj: Adjacent Matrix
            |source |target |weight |
            ...
        File_2: sbm_<# of nodes>n_cmt: Corre. Commnuities
            |node_id | community_id |
            ...
    Args:
        node_num, community_num: intuitive
        inblock_prob: prob. of edges between nodes from the same cmt.
        crossblock_prob: prob. of edges ... different cmt.
        community_size: appoint the size of multiple cmt. (i.e. [497,503])
        *nodes_to_purturb: # of nodes to change their cmt.
    '''

    def __init__(self, node_num, community_num, community_id=1, nodes_to_purturb=5, inblock_prob=0.1, crossblock_prob=0.01, community_size=None):
        self._node_num = node_num
        self._community_num = community_num
        self._community_id = community_id
        self._nodes_to_purturb=nodes_to_purturb
        self._graph = None
        self._chngnodes = None
        self._inblock_prob = inblock_prob
        self._crossblock_prob = crossblock_prob
        self.set_mtx_B(inblock_prob, crossblock_prob)
        self.sample_node_community(community_size) # specify cmt_size if not, appoint cmt_id to each node

    def set_mtx_B(self, inblock_prob=0.1, crossblock_prob=0.01):
        self._B = np.ones((self._community_num, self._community_num)) * crossblock_prob
        for i in range(self._community_num):
            self._B[i, i] = inblock_prob

        return self._B

    def sample_graph(self):
        self._graph = nx.DiGraph() # empty graph
        # add nodes
        self._graph.add_nodes_from(range(self._node_num))
        # add edges
        for i in range(self._node_num):
            for j in range(i):
                prob = self._B[self._node_community[i], self._node_community[j]]
                if np.random.uniform() <= prob:
                    self._graph.add_edge(i, j)
                    self._graph.add_edge(j, i) # directed graph

        nodes= [i for i in range(self._node_num) if self._node_community[i]==self._community_id]
        self._chngnodes = random.sample(nodes, self._nodes_to_purturb)

        return self._graph


    def sample_node_community(self, community_size=None):
        if community_size is None:
            community_size = np.random.multinomial(self._node_num, [1.0 / self._community_num] * self._community_num)
        print("community_size", community_size)

        self._node_community = []
        assert(len(community_size) == self._community_num) # test if the input is legal
        for i, size in enumerate(community_size):
            self._node_community += [i] * size # list of cmt_id by increasing order

    def save_as_csv(self):
        # file 1
        filename1 = 'sbm_' + str(self._node_num) + 'n_adj.csv'
        dict_list1 = []
        sorted_edges = sorted(self._graph.edges(), key=lambda x: (x[0], x[1]))
        for _, edge in enumerate(sorted_edges):
            tmp_dict = dict(source=edge[0], target=edge[1], weight=1)
            dict_list1.append(tmp_dict)

        with open(filename1, 'w') as f:
            fieldnames = ['source', 'target', 'weight']
            f_csv = csv.DictWriter(f, fieldnames)
            f_csv.writeheader()
            f_csv.writerows(dict_list1)

        # file2
        filename2 = 'sbm_' + str(self._node_num) + 'n_cmt.csv'
        dict_list2 = []
        for i in range(self._node_num):
            tmp_dict = dict(node_id=i, community_id=self._node_community[i])
            dict_list2.append(tmp_dict)

        with open(filename2, 'w') as f:
            fieldnames = ['node_id', 'community_id']
            f_csv = csv.DictWriter(f, fieldnames)
            f_csv.writeheader()
            f_csv.writerows(dict_list2)


if __name__ == '__main__':
    my_graph = SBMGraph(1000, 2, inblock_prob=0.2, crossblock_prob=0.05, community_size=[500, 500])
    my_graph.sample_graph() # generate graph according to prob.
    my_graph.save_as_csv()