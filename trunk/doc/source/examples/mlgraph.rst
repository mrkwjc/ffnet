-------------------
Standard multilayer
-------------------

.. plot::
    :include-source:

    from ffnet import mlgraph, ffnet
    import networkx as NX
    import pylab

    conec = mlgraph((3,6,3,2), biases=False)
    net = ffnet(conec)
    NX.draw_graphviz(net.graph, prog='dot')
    pylab.show()

