# Forked from palash1992/DynamicGEM

import networkx as nx
import csv
import random
import numpy as np

from SBM_gen import SBMGraph


def diminish_community(sbm_graph, community_id, nodes_to_purturb, chngnodes):
    n = sbm_graph._node_num
    community_nodes = [i for i in range(n) if sbm_graph._node_community[i] == community_id]
    nodes_to_purturb = min(len(community_nodes), nodes_to_purturb)
    perturb_nodes = chngnodes

    left_communitis = [i for i in range(sbm_graph._community_num) if i != community_id]
    for node_id in perturb_nodes:
        corre_edges_adjust(sbm_graph, node_id) # add 40 edges & remove
        new_community = random.sample(left_communitis, 1)[0]
        print('Node %d change from community %d to %d' % (node_id,
                                                          sbm_graph._node_community[node_id],
                                                          new_community))
        # assign new cmt_id
        sbm_graph._node_community[node_id] = new_community

    nodes = [i for i in range(n) if sbm_graph._node_community[i] == community_id]
    chngnodes = random.sample(nodes, nodes_to_purturb)

    return perturb_nodes, chngnodes


def corre_edges_adjust(sbm_graph, node_id):
    if sbm_graph._graph is None:
        sbm_graph.sample_graph()
    else:
        n = sbm_graph._node_num
        othercommnodes = [i for i in range(n) if sbm_graph._node_community[i] != sbm_graph._node_community[node_id] if
                          not sbm_graph._graph.has_edge(node_id, i)]
        edgesnodes = random.sample(othercommnodes, 40) # 500 * (0.1-0.01) ~= 40
        for i in edgesnodes:
            sbm_graph._graph.add_edge(node_id, i)
            sbm_graph._graph.add_edge(i, node_id)

        for i in range(n):
            if i == node_id:
                continue
            # cmt_id not changed yet
            if sbm_graph._node_community[i] == sbm_graph._node_community[node_id]:
                if sbm_graph._graph.has_edge(node_id, i):
                    # the proportion of edges to preserve
                    prob = sbm_graph._crossblock_prob / sbm_graph._inblock_prob
                    if np.random.uniform() >= prob:
                        sbm_graph._graph.remove_edge(node_id, i)
                        sbm_graph._graph.remove_edge(i, node_id)


def get_community_diminish_series(node_num, cmt_num, nodes_to_purturb, inblock_prob, crossblock_prob,
                                     community_id, length):
    my_graph = SBMGraph(node_num, cmt_num,
                        inblock_prob = inblock_prob,
                        crossblock_prob = crossblock_prob,
                        community_id = community_id,
                        community_size = [int(node_num/2), node_num - int(node_num/2)],
                        nodes_to_purturb = nodes_to_purturb) # empty graph, edges not sampled yet
    my_graph.sample_graph() # initial graph
    chngnodes = my_graph._chngnodes

    graphs = [my_graph._graph.copy()]
    nodes_comunities = [my_graph._node_community[:]] # list of node cmt_id lists
    perturbations = [[]]
    dyn_change_nodes = [[]]

    for i in range(length - 1):
        print('Timestamp %d' % (i+1))

        print("Migrating Nodes:")
        print(chngnodes)
        perturb_nodes, chngnodes = diminish_community(my_graph,
                                                      community_id,
                                                      nodes_to_purturb, # num of nodes to change
                                                      chngnodes)
        print("Nodes to migrate next:")
        print(chngnodes)
        perturbations.append(perturb_nodes)
        dyn_change_nodes.append(chngnodes)

        graphs.append(my_graph._graph.copy()) # dyngraph series list
        nodes_comunities.append(my_graph._node_community[:]) # corrseponding cmt_id of nodes

    # return the list of dynamic graph
    return graphs, nodes_comunities


def save_as_csv(graph, nodes_comunities):
    '''
    Function:
        Receive a series of dynSBM Graphs, save as csv files
    Args:
        graph: a list of networkx graph pbject
        nodes_comunities: corresponding cmt_id list for each graph
    '''
    for k in range(len(graph)):
        # file1
        filename1 = 'sbm_' + str(graph[k].number_of_nodes()) + 'n_adj_t' + str(k) + '.csv'
        dict_list1 = []
        sorted_edges = sorted(graph[k].edges(), key=lambda x: (x[0], x[1]))
        for _, edge in enumerate(sorted_edges):
            tmp_dict = dict(source=edge[0], target=edge[1], weight=1)
            dict_list1.append(tmp_dict)

        with open(filename1, 'w') as f:
            fieldnames = ['source', 'target', 'weight']
            f_csv = csv.DictWriter(f, fieldnames)
            f_csv.writeheader()
            f_csv.writerows(dict_list1)

        # file2
        filename2 = 'sbm_' + str(graph[k].number_of_nodes()) + 'n_cmt_t' + str(k) + '.csv'
        dict_list2 = []
        for i in range(graph[k].number_of_nodes()):
            tmp_dict = dict(node_id=i, community_id=nodes_comunities[k][i])
            dict_list2.append(tmp_dict)

        with open(filename2, 'w') as f:
            fieldnames = ['node_id', 'community_id']
            f_csv = csv.DictWriter(f, fieldnames)
            f_csv.writeheader()
            f_csv.writerows(dict_list2)



if __name__ == '__main__':
    node_num = 1000
    cmt_num = 2
    nodes_to_purturb = 10
    length = 5
    inblock_prob = 0.1
    crossblock_prob = 0.01
    graphs, nodes_comunities = get_community_diminish_series(node_num = node_num,
                                    cmt_num = cmt_num,
                                    nodes_to_purturb = nodes_to_purturb,
                                    inblock_prob = inblock_prob,
                                    crossblock_prob = crossblock_prob,
                                    community_id = 1, # which cmt the nodes change from
                                    length = length) # num of dyn graphs
    save_as_csv(graphs, nodes_comunities)