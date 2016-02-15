#-*- coding: utf-8 -*-

########################################################################
## Copyright (c) 2011-2015 Marek Wojciechowski 
## <mwojc@p.lodz.pl>
##
## Distributed under the terms of GPL-3.0 license
## https://opensource.org/licenses/GPL-3.0
########################################################################

#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from version import version as ffnetui_version

from pyface.image_resource import ImageResource
from pyface.api import AboutDialog

about = AboutDialog(parent = None,
                    image = ImageResource('ffnetui256x256'),
                    additions = ['<b>ffnetui-%s</b>' %ffnetui_version,
                                 'This is user interface for ffnet - ',
                                 'feed-forward neural network for python',
                                 '<a href=ffnet.sourceforge.net>http://ffnet.sourceforge.net</a>',
                                 '',
                                 'Copyright &copy; 2005-2016', '<b>Marek Wojciechowski</b>',
                                 'Technical University of Lodz, Poland',
                                 '<a href=mailto:mwojc@p.lodz.pl>mwojc@p.lodz.pl</a>',
                                 '',
                                 'Distributed under GPL-3.0 license',
                                 '<a href=opensource.org/licenses/GPL-3.0>https://opensource.org/licenses/GPL-3.0</a>',
                                 '',
                                 ''])

if __name__ == "__main__":
    about.open()