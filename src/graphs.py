########################################################################
##  Copyright (C) 2008 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################

"""
Acyclic directed graphs

This module contains implementation of acyclic directed graph,
i.e. ADiGraph class, based on DiGraph from networkx project and
generators of such graphs.
"""
import networkx as NX
from networkx import DiGraph

class ADiGraph(DiGraph):
    def __init__(self, conec=[],  **kwargs):
        """
        Calls DiGraph constructor and checks if the graph is connected and acyclic
        """
        DiGraph.__init__(self, **kwargs)
        DiGraph.add_edges_from(self, conec)
        #self.add_edges_from(conec)  #copy maximum recursion here
        if not self._is_connected(): raise ValueError("Not connected graph")
        if not self._is_directed_acyclic_graph(): raise ValueError("Not acyclic graph")

    def _is_connected(self):
        if self.order() == 0:
            return True #Only for initial empty graph
        elif self.order() == 1:
            return False #Cannot exist single node
        else: #check only if there are some nodes in graph
            return NX.is_connected(self.to_undirected())

    def _is_directed_acyclic_graph(self):
        return NX.dag.is_directed_acyclic_graph(self)

    def topologically_sorted_nodes(self):
        """
        Returns nodes ordered topologically
        """
        return NX.dag.topological_sort(self)

    def snodes(self):
        """
        Alias to topologically_sorted_nodes
        """
        return self.topologically_sorted_nodes()

    def snodeno(self):
        """
        Returns list of triples: (node, num. of preds, num. of succs)
        """
        sno = []
        for node in self.snodes():
            sno.append((node, self.in_degree(node), self.out_degree(node)))
        return sno

    def predsno(self):
        """
        List of predecessors for snodes with its conection position in conec
        """
        pno = []
        conec = self.conec()
        for node in self.snodes():
            for pred in self.predecessors(node):
                pno.append((pred, conec.index((pred, node))))
        return pno

    def succsno(self):
        """
        List of successors for snodes with its conection position in conec
        """
        sno = []
        conec = self.conec()
        for node in self.snodes():
            for succ in self.successors(node):
                sno.append((succ, conec.index((node, succ))))
        return sno

    def topologically_sorted_edges(self):
        """
        Returns edges ordered for topologically sorted nodes
        """
        edges = []
        for node in self.topologically_sorted_nodes():
            edges += self.in_edges(node)
        return edges

    def conec(self):
        """
        Alias to topologically_sorted_edges
        """
        return self.topologically_sorted_edges()

    def sources(self):
        """
        Returns sources of the graph
        """
        inno = []
        for node in self.nodes_iter():
            if not self.in_edges(node):
                inno.append(node)
        inno.sort()
        return inno

    def sinks(self):
        """
        Returns sinks of the graph
        """
        outno = []
        for node in self.nodes_iter():
            if not self.out_edges(node):
                outno.append(node)
        outno.sort()
        return outno

    def hiddens(self):
        """
        Returns all intermediate nodes in the graph
        """
        hidno = []
        for node in self.nodes_iter():
            if self.out_edges(node) and self.in_edges(node):
                hidno.append(node)
        hidno.sort()
        return hidno

    def add_node(self,  n):
        raise ValueError("Adding nodes not allowed. Use add_edge instead")

    def add_nodes_from(self,  nlist):
        raise ValueError("Adding nodes not allowed. Use add_edges_from instead")

    def add_edge(self,  u,  v = None):
        temp = self.copy()
        DiGraph.add_edge(temp,  u,  v = v)
        if not temp._is_directed_acyclic_graph():
            raise ValueError("Edge (%s, %s) creates a cycle" %(u, v) )
        elif not temp._is_connected():
            raise ValueError("Edge (%s, %s) creates disconnected graph" %(u, v) )
        else:
            DiGraph.add_edge(self,  u,  v = v)

    def add_edges_from(self,  ebunch):
        temp = self.copy()
        DiGraph.add_edges_from(temp, ebunch)
        if not temp._is_directed_acyclic_graph():
            raise ValueError("Edges %s create a cycle" %(ebunch, ) )
        elif not temp._is_connected():
            raise ValueError("Edges %s create disconnected graph" %(ebunch, ) )
        else:
            DiGraph.add_edges_from(self,  ebunch)

    def add_path(self, nlist):
        ebunch = []
        fromv = nlist[0]
        for tov in nlist[1:]:
            ebunch.append((fromv,tov))
            fromv=tov
        self.add_edges_from(ebunch)

    def add_cycle(self,  nlist):
        raise ValueError("Adding cycles not allowed.")

    def remove_node(self, n):
        """
        Remove node n from graph if the deletion do not disconnect graph.
        Attempting to delete a non-existent node will raise an exception.
        """
        temp = self.copy()
        DiGraph.remove_node(temp,  n)
        if temp._is_connected():
            DiGraph.remove_node(self,  n)
        else: raise ValueError("Node %s disconnects graph" %(n, ) )

    def remove_nodes_from(self, nlist):
        """
        Remove nodes in nlist from graph if the deletion do not disconnect graph.
        Attempting to delete a non-existent node will raise an exception.
        """
        temp = self.copy()
        DiGraph.remove_nodes_from(temp,  nlist)
        if temp._is_connected():
            DiGraph.remove_nodes_from(self,  nlist)
        else: raise ValueError("Nodes %s disconnect graph" %(nlist, ) )

    def remove_edge(self, u,  v = None):
        temp = self.copy()
        DiGraph.remove_edge(temp, u, v = v)
        if not temp._is_connected():
            raise ValueError("Removing edge (%s, %s) creates disconnected graph" %(u, v) )
        else:
            DiGraph.remove_edge(self, u, v = v)

    def remove_edges_from(self,  ebunch):
        temp = self.copy()
        DiGraph.remove_edges_from(temp, ebunch)
        if not temp._is_connected():
            raise ValueError("Removing edges %s creates disconnected graph" %(ebunch, ) )
        else:
            DiGraph.remove_edges_from(self,  ebunch)

    def reverse(self, copy = True):
        """
        Return a new graph with the same vertices and edges
        but with the directions of the edges reversed.

        Why not to leave DiGraph.reverse?
        """
        H=self.__class__() # new empty ADiGraph
        H.add_edges_from([(v,u) for (u,v) in self.edges_iter()]) #this is enough, all nodes are connected
        return H

    def depgraph(self, u, v = None, reverse = False):
        """
        Returns subgraph which connects node u with v.
        Returns empty graph if there is no dependency between nodes.
        """
        if reverse: H = self.reverse(copy = True)
        else: H = self.copy()
        node_removal = 1
        while node_removal:
            node_removal = 0
            for node in H.nodes():
                if not H.in_degree(node) and node != u or \
                            not H.out_degree(node) and node != v and v != None:
                    try:
                        H.remove_node(node)
                        node_removal = 1
                    except:
                        raise ValueError("No such depgraph exists")
        return H

    def subgraph(self, nbunch):
        H = DiGraph.subgraph(self, nbunch) # first use
        G = self.__class__(H.edges())
        return G

###########
## TESTS ##
###########
import unittest
class TestADigraph(unittest.TestCase):
    def setUp(self):
        self.g = ADiGraph()
        self.conec = [(1, 3), (2, 3), (0, 3), (1, 4), (2, 4), (0, 4), (3, 5), (4, 5), (0, 5)]
        self.conecr = [(1, 3), (2, 3), (0, 3), (1, 4), (2, 4), (0, 4), (3, 5), (4, 5), (0, 5),  (5,  1)]

    def testAddEdge(self):
        self.g.add_edge(1, 2)
        self.assertEqual(self.g.edges(),  [(1, 2)])
        #self.assertRaises(ValueError,  self.g.add_edge,   (1, 1))

    def testAddEdgesFrom1(self):
        self.g.add_edges_from(self.conec)
        self.assertEqual(set(self.g.edges()),  set(self.conec))
        self.assertRaises(ValueError,  self.g.add_edge,  5, 1)
        self.assertRaises(ValueError,  self.g.add_edge,  7, 8)

    def testAddEdgesFrom2(self):
        self.assertRaises(ValueError, self.g.add_edges_from, self.conecr)

    def testInit(self):
        self.assertRaises(ValueError, ADiGraph, self.conecr)

    def testAddNode(self):
        self.assertRaises(ValueError, self.g.add_node, 8)

    def testAddNodesFrom(self):
        self.assertRaises(ValueError, self.g.add_nodes_from, [8, 9])

    def testAddPath(self):
        self.g.add_edges_from(self.conec)
        self.g.add_path([11, 7, 5,  6])
        self.assertEqual(set(self.g.edges()),  set(self.conec+[(11, 7), (7, 5), (5, 6)]))
        self.assertRaises(ValueError, self.g.add_path, [8, 9, 10])

    def testAddCycle(self):
        self.assertRaises(ValueError, self.g.add_cycle, [1, 2, 3])

    def testRemoveNode(self):
        self.g.add_edges_from(self.conec)
        self.g.remove_node(3)
        self.assertEqual(set(self.g.edges()),  set([(1, 4), (2, 4), (0, 4), (4, 5), (0, 5)]))
        self.assertRaises(ValueError, self.g.remove_node, 4)

    def testRemoveNodesFrom(self):
        self.g.add_edges_from(self.conec)
        self.g.remove_nodes_from([0, 3])
        self.assertEqual(set(self.g.edges()),  set([(1, 4), (2, 4), (4, 5)]))
        self.assertRaises(ValueError, self.g.remove_nodes_from, [1, 4])

    def testRemoveEdge(self):
        self.g.add_edges_from(self.conec)
        self.g.remove_edge(3, 5)
        self.assertEqual(set(self.g.edges()),  \
                                            set([(1, 3), (2, 3), (0, 3), (1, 4), (2, 4), (0, 4), (4, 5), (0, 5)]))
        self.g.remove_edge(4, 5)
        #self.g.delete_edge(0, 5) #also 5 node should be removed??
        self.assertRaises(ValueError, self.g.remove_edge, 0, 5)

    def testRemoveEdgesFrom(self):
        self.g.add_edges_from(self.conec)
        self.g.remove_edges_from([(0, 3), (1, 3), (2, 3), (0, 5)])
        self.assertEqual(set(self.g.edges()),  \
                                            set([(3, 5), (4, 5), (1, 4), (2, 4), (0, 4)]))
        self.assertRaises(ValueError, self.g.remove_edges_from, [(4, 5)])

    def testTopologicallySortedNodes(self):
        self.g.add_edges_from(self.conec)
        self.g.add_edge(8, 0)
        sedges = self.g.conec()
        self.assertEqual(set(sedges[:1]), set([(8, 0)]))
        self.assertEqual(set(sedges[1:7]), set([(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4)]))
        self.assertEqual(set(sedges[7:]), set([(0, 5), (3, 5), (4, 5)]))

    def testSourcesHiddensSinks(self):
        self.g.add_edges_from(self.conec)
        self.g.add_edge(0, 10)
        self.assertEqual(self.g.sources(), [0, 1, 2])
        self.assertEqual(self.g.sinks(), [5, 10])
        self.assertEqual(self.g.hiddens(), [3, 4])

#    def testLayers(self):
#        self.g.add_edges_from(self.conec)
#        self.g.add_edge(1, 5)
#        layers = self.g.layers()
#        self.assertEqual(layers, [[0, 1, 2], [3, 4], [5]])

    def testDepGraph(self):
        self.g.add_edges_from(self.conec)
        h = self.g.depgraph(1, 5)
        self.assertEqual(set(h.edges()), set([(1, 3), (1, 4), (3, 5), (4, 5)]))
        self.g.add_edges_from([(3, 6), (4, 6)])
        h = self.g.depgraph(1)
        self.assertEqual(set(h.edges()), set([(1, 3), (1, 4), (3, 5), (4, 5), (3, 6), (4, 6)]))
        self.assertRaises(ValueError, self.g.depgraph, [5, 1])
        h = self.g.depgraph(5, 1, reverse = True)
        self.assertEqual(set(h.edges()), set([(3, 1), (4, 1), (5, 3), (5, 4)]))

    def testSubGraph(self):
        self.g.add_edges_from(self.conec)
        h = self.g.subgraph([1, 3, 5])
        self.assertEqual(set(h.edges()), set([(1, 3), (3, 5)]))
        self.g.add_edges_from([(5, 6), (6, 7)])
        self.assertRaises(ValueError, self.g.subgraph, [0, 3, 6, 7])

# run tests
if __name__ == '__main__':
    unittest.main()
