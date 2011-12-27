.. image:: http://images.sourceforge.net/images/project-support.jpg
    :target: http://sourceforge.net/donate/index.php?group_id=182429

.. title:: Feed-forward neural network for python

==============================================
Feed-forward neural network for python (ffnet)
==============================================

:Author: `Marek Wojciechowski <mwojc.html>`_
:Version: `0.7 <http://sourceforge.net/projects/ffnet/files/ffnet/ffnet-0.7>`_
:License: `GPL <http://www.gnu.org/copyleft/gpl.html>`_

----
News
----

*27/12/2011*

You can look now at the growing list of publications_ which cite ffnet.

*09/08/2011*

ffnet version 0.7 has been released and is available for download at https://sourceforge.net/projects/ffnet.
This release contains couple of important changes:
    
    * neural network can be trained now using the power of multi-processor systems (see example mptrain.py_)
    * attributes which are necessary for calculation of network derivatives are now generated only on demand;
    * data normalization limits are not changed when retrainig with new data set; net.renormalize = True have to be set first;
    * compatibility with newest versions of numpy, scipy and networkx is enhanced;
    * support for *export to java* and *drawing network with drawffnet* is dropped.

Basic API is left almost untouched. Exactly the same trainig scripts as for older versions should work without problems. 

`Older news <older_news.html>`_

--------
Overview
--------

ffnet is a fast and easy-to-use feed-forward neural
network training solution for python.

Unique features:
    1. Any network connectivity without cycles is allowed.
    2. Training can be performed with use of several optimization schemes including: standard backpropagation with momentum, rprop, conjugate gradient, bfgs, tnc (with multiprocessing), genetic alorithm based optimization.
    3. There is access to exact partial derivatives of network outputs vs. its inputs.
    4. Automatic normalization of data.

Basic assumptions and limitations:
    1. Network has feed-forward architecture.
    2. Input units have identity activation function, all other units have sigmoid activation function.
    3. Provided data are automatically normalized, both input and output, with a linear mapping to the range (0.15, 0.85). Each input and output is treated separately (i.e. linear map is unique for each input and output).
    4. Function minimized during training is a sum of squared errors of each output for each training pattern.
   
Performance:
    Excellent computational performance is achieved implementing core functions in fortran 77 and wrapping them with f2py. ffnet outstands in performance pure python training packages and is competitive to 'compiled language' software. Incorporation of multiprocessing capabilities (tnc algorithm so far) makes ffnet ideal for large scale (really!) problems. Moreover, a trained network can be exported to fortran sources, compiled and called from many programming languages.

Usage:

.. Basic usage of the package is outlined below. Read package docstrings and examples for more info.

::

    from ffnet import ffnet, mlgraph, savenet, loadnet, exportnet
    conec = mlgraph( (2,2,1) )
    net = ffnet(conec)
    input = [ [0.,0.], [0.,1.], [1.,0.], [1.,1.] ]
    target  = [ [1.], [0.], [0.], [1.] ]
    net.train_tnc(input, target, maxfun = 1000)
    net.test(input, target, iprint = 2)
    savenet(net, "xor.net")
    exportnet(net, "xor.f")
    net = loadnet("xor.net")
    answer = net( [ 0., 0. ] )
    partial_derivatives = net.derivative( [ 0., 0. ] )

--------
Examples
--------

Training script examples (included in the source distribution):
    1. Pattern recognition example: `ocr.py <examples/ocr.html>`_ [plots: `digit2 <figures/digit2.png>`_, `digit7 <figures/digit7.png>`_].
    2. Sine training example: `sin.py <examples/sin.html>`_ [plot: `sincos <figures/sincos.png>`_].
    3. XOR problem example: `xor.py <examples/xor.html>`_ [generated fortan source `xor.f <examples/xor.f.html>`_].
    4. Emulating Black-Scholes stock prices: `stock.py <examples/stock.html>`_ [plot: `fitness <figures/fitness.png>`_].
    5. Parallel training example: `mptrain.py <examples/mptrain.html>`_ [plot: `speedup <figures/speedup.png>`_]. 

Network architecture examples:
    1. `mlgraph <figures/mlgraph.png>`_ (standard multilayer)
    2. `tmlgraph <figures/tmlgraph.png>`_
    3. `imlgraph <figures/imlgraph.png>`_

-------------
Documentation
-------------

At the moment you are encouraged to read package docstrings. 

--------
Download
--------

Go to sourceforge download page: http://sourceforge.net/projects/ffnet/files/ffnet for release versions of ffnet.

You can also checkout development version of the code from the project subversion repository:

::

    svn co https://ffnet.svn.sourceforge.net/svnroot/ffnet/trunk ffnet

or from this direct link: http://ffnet.svn.sourceforge.net/viewvc/ffnet/trunk.tar.gz


------------
Installation
------------

Installation instructions can be found in `README <http://sourceforge.net/projects/ffnet/files/ffnet/ffnet-0.7/README>`_.

--------------
Reporting bugs
--------------

Bug tracker, forum and a mailing list are avilable at https://sourceforge.net/projects/ffnet 

------------
Citing ffnet
------------

ffnet was created *in the hope that it will be useful*. If you find it really is
and you are going to publish some ffnet generated results, please cite it:

::

    \bibitem[FFNET, 2011]{FFNET} Wojciechowski, M.,
    Feed-forward neural network for python,
    Technical University of Lodz (Poland),
    Department of Civil Engineering, Architecture and Environmental Engineering,
    http://ffnet.sourceforge.net/, ffnet-0.7, August 2011

You can also look at the growing list of `publications <ffnet-publications.html>`_ which cite ffnet.

..
  .. image:: http://sflogo.sourceforge.net/sflogo.php?group_id=126615&type=8
      :target: http://sourceforge.net

.. image:: http://images.sourceforge.net/images/project-support.jpg
    :target: http://sourceforge.net/donate/index.php?group_id=182429


.. Google analytics code

.. raw:: html

    <script type="text/javascript">

    var _gaq = _gaq || [];
    _gaq.push(['_setAccount', 'UA-5523152-1']);
    _gaq.push(['_trackPageview']);

    (function() {
        var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
        ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
        var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
    })();

    </script>
