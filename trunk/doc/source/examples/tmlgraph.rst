--------------------------
Fully connected multilayer
--------------------------

.. plot::
    :include-source:

    from ffnet import tmlgraph, ffnet
    import networkx as NX
    import pylab

    conec = tmlgraph((3,6,3), biases=False)
    net = ffnet(conec)
    NX.draw_graphviz(net.graph, prog='dot')
    pylab.show()

