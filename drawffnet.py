from pylab import *
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib.patches import Circle

import networkx as NX

# General function making network plot
def drawffnet(net, biases = False):
    """
    Takes ffnet object and draws the network. 
    Networkx layouts and maplotlib buttons are used to control layout. 
    
    Note:
    This is draft solution.
    Function seems not to work with older versions of matplotlib 
    (below 0.87.7, e.g. in enthought python we have 0.87.3 and
    there are problems). There might occur also problems
    with graphviz layouts on Windows.
    """
    
    #Takes copies of network graphs
    G = net.graph.copy()
    if not biases: G.delete_node(0)
    BG = net.bgraph.copy()
    
    
    ax = subplot(111)
    subplots_adjust(left=0.25)
    setp(ax, xticks=[], yticks=[])
    try:
        layout = NX.graphviz_layout(G, prog='dot')
        active = 0
    except:
        layout = NX.circular_layout(G)
        active = 5
    NX.draw_networkx(G, layout)
    
    # Make radio buttons for layouts
    axcolor = 'lightgoldenrodyellow'
    
    rax = axes([0.025, 0.4, 0.18, 0.35], axisbg=axcolor)
    setp(rax, xticks=[], yticks=[])
    
    text(0., 1., "Network layouts")
    radio_layout = RadioButtons(rax, \
                    ('dot', 'neato', 'fdp', 'twopi', 'circo', \
                    'circular', 'random', 'spring', 'spectral', 'shell'), \
                    active=active)
    radio_layout.layout = layout
    def layoutfunc(label):
        ax.clear()
        setp(ax, xticks=[], yticks=[])
        try:
            if label == 'dot': layout = NX.graphviz_layout(G, prog='dot')
            if label == 'neato': layout = NX.graphviz_layout(G, prog='neato')
            if label == 'fdp': layout = NX.graphviz_layout(G, prog='fdp')
            if label == 'twopi': layout = NX.graphviz_layout(G, prog='twopi')
            if label == 'circo': layout = NX.graphviz_layout(G, prog='circo')
            if label == 'circular': layout = NX.circular_layout(G)
            if label == 'random': layout = NX.random_layout(G)
            if label == 'spring': layout = NX.spring_layout(G, iterations=15)
            if label == 'spectral': layout = NX.spectral_layout(G, iterations=50)
            if label == 'shell': layout = NX.shell_layout(G)
    
            radio_layout.layout = layout
            NX.draw_networkx(G, layout)
            draw()
        except:
            setp(ax, xlim = (0,1), ylim = (0,1))
            text(0.5, 0.5, "Layout is not avilable.\n(Not working graphviz?)", \
                fontsize=14, color='r', horizontalalignment='center')
    radio_layout.on_clicked(layoutfunc)
    
    # Make a button for showing adjoint network (backpropagation network)
    bgraphax = axes([0.025, 0.3, 0.18, 0.04])
    button1 = Button(bgraphax, 'Backprop graph', color=axcolor, hovercolor='0.975')
    def showbgraph(event):
        ax.clear()
        setp(ax, xticks=[], yticks=[])
        layout = radio_layout.layout
        NX.draw_networkx(G, layout, alpha=0.1, labels={})
        NX.draw_networkx(BG, layout, node_color='y')
        draw()
    button1.on_clicked(showbgraph)
    
    # Make a button for showing derivative networks
    dgraphax = axes([0.025, 0.2, 0.18, 0.04])
    button2 = Button(dgraphax, 'Diff graphs', color=axcolor, hovercolor='0.975')
    def showdgraphs(event):
        def dsubgraph_nodes(inp, out, nbunch):
            pred = NX.predecessor(G, inp, out)
            nbunch += pred
            for node in pred:
                dsubgraph_nodes(inp, node, nbunch)
            return nbunch
        layout = radio_layout.layout
        import time
        for innode in net.inno:
            for outnode in net.outno:               
                nbunch = [outnode]
                nbunch = dsubgraph_nodes(innode, outnode, nbunch)
                g = G.subgraph(nbunch)
                ax.clear()
                setp(ax, xticks=[], yticks=[])
                NX.draw_networkx(G, layout, alpha=0.1, labels={})
                NX.draw_networkx(g, layout, node_color='c')
                draw()
                time.sleep(3)
    button2.on_clicked(showdgraphs)
    
    axes()
    
# Test the thetwork
if __name__ == "__main__":
    from ffnet import ffnet, mlgraph, tmlgraph
    
    ##conec = mlgraph((3,5,5,3), biases = False)
    from ffnet import imlgraph
    conec = imlgraph((3,[(3,), (6,3), (3,)],3))
    net = ffnet(conec)
    
    drawffnet(net)
    show()