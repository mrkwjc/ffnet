--------
**News**
--------
*15/02/2015*
    ffnet version 0.8.0 has been released with python 3 support. Only minor changes in code (and no API changes) are made in comparison to previous release, all scripts should run without problems.

----

*07/01/2012*
    ffnet version 0.7.1 has been released. This release contains mainly documentation improvements and changes in examples. Look also at the new sphinx-based website: http://ffnet.sourceforge.net.

----

*27/12/2011*
    You can look now at the growing list of :download:`publications <pubs/ffnet-publications.html>` which cite ffnet.

----

*09/08/2011*
    ffnet version 0.7 has been released and is available for download at https://sourceforge.net/projects/ffnet. This release contains couple of important changes:
    
    * neural network can be trained now using the power of multi-processor systems (see example mptrain.py)
    * attributes which are necessary for calculation of network derivatives are now generated only on demand;
    * data normalization limits are not changed when retrainig with new data set; net.renormalize = True have to be set first;
    * compatibility with newest versions of numpy, scipy and networkx is enhanced;
    * support for *export to java* and *drawing network with drawffnet* is dropped.

    Basic API is left almost untouched. Exactly the same trainig scripts as for older versions should work without problems. 

----

*28/10/2009*
    ffnet version 0.6.2 is released and is available for download at https://sourceforge.net/projects/ffnet/files. This release contains minor enhancements and compatibility improvements: 

    * ffnet works now with >=networkx-0.99; 
    * neural network can be called now with 2D array of inputs, it also returns numpy array instead of python list; 
    * readdata function is now alias to numpy.loadtxt; 
    * docstrings are improved. 

----

*29/04/2009*
    New release of ffnet is coming. It will resolve, among others, compatibility problem with the newest versions of networkx. Until then (if you run into this compatibility problem) you can try to download and install ffnet from its svn repository. Direct link to the trunk: 

    http://ffnet.svn.sourceforge.net/viewvc/ffnet/trunk.tar.gz

----

*23/10/2007*
    ffnet 0.6.1 released! Source packages, Gentoo ebuilds and Windows binaries are available for download at:

    http://sourceforge.net/projects/ffnet

    This is mainly bugfix release.

    New features:

    * added 'readdata' function (simplifies reading training data
      from ASCII files)

    Changes & bug fixes:

    * fixed bug preventing ffnet form working with scipy-0.6
    * importing ffnet doesn't need matplotlib now (really)
    * corrections in fortran code generators

----

*01/10/2007*
    The maintance release 0.6.1 is planned in the nearest feature, as the new version of scipy (0.6) has been released. Unfortunately new scipy has one, but important, incompatibility with ffnet. Currently, if you need ffnet fully working with scipy-0.6 you need to download svn version.

----

*22/03/2007*
    ffnet 0.6 released! Source packages, Gentoo ebuilds and Windows binaries are now available for download at:

    http://sourceforge.net/projects/ffnet

    Changes since 0.5 version:

    New features:

    * trained network can be now exported to fortran source code and compiled
    * added new architecture generator (imlgraph)
    * added rprop training algorithm
    * added draft network plotting facility (based on networkx and matplotlib)

    Changes & bug fixes:

    * fixed bug preventing ffnet form working with networkx-0.33
    * training data can be now numpy arrays
    * ffnet became a package now, but API should be compatibile with previous version

    Documentation:

    * docstrings of all objects have been improved
    * docs (automatically generated with epydoc) are avilable
      online and have been included to source distribution

----

*02/02/2007*
    Documentation of ffnet modules (automatically generated with epydoc) is now  avilable online. You may browse it following the link: 
    
    http://ffnet.sourceforge.net/doc/index.html

----

*13/12/2006*
    Ebuilds for ffnet-0.5 and networkx-0.33 for Gentoo Linux users avilable for download. 


.. |STAR| image:: pictures/redstar.png
    :scale: 8%