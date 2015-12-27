import networkx as nx
import numpy as np

def layered_layout(G):
    topological_sort = nx.topological_sort(G)
    n = len(topological_sort)
    pos = np.zeros((n, 2))
    posdict = {}
    nxp, nyp, ip = -2, -2, 0
    for i, node in enumerate(topological_sort):
        nx_, ny = pos[i]
        if nx_ > nxp:  # New layer
            layery = pos[ip:i, 1]  # y coors of nodes in layer
            layery[:] = layery[:] - (len(layery)-1)  # shift node positions
            nyp = -2  # Reset y coor
            ip = i # Set new layer start
            nxp = nx_
        else:
            pos[i, 0] = nxp  # Never go back 
        ny = nyp + 2
        pos[i, 1] = ny
        nyp = ny
        # Assure successors are beyond
        successors = G.successors(node)
        for snode in successors:
            j = topological_sort.index(snode)
            sx, sy = pos[j]
            if sx <= nx_:  # Node not handled before
                sx = nx_ + 2
            pos[j, 0] = sx
        posdict[node] = pos[i]
    # Shift last layer
    layery = pos[ip:n, 1]
    layery[:] = layery[:] - (len(layery)-1)
    return posdict

if __name__ == "__main__":
    #from ffnet import mlgraph, tmlgraph
    #conec = tmlgraph((1,2,1,1,2), biases = False)
    #G = nx.DiGraph()
    #G.add_edges_from(conec)
    def randdag():
        G = nx.gnp_random_graph(20,0.5,directed=True)
        DAG = nx.DiGraph([(u,v) for (u,v) in G.edges() if u<v])
        return DAG
    G = randdag()
    pos = layered_layout(G)
    nx.draw_networkx(G, pos)