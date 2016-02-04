#-*- coding: utf-8 -*-
#from traits.etsconfig.api import ETSConfig
#ETSConfig.toolkit = 'qt4'

from pyface.image_resource import ImageResource
from pyface.api import AboutDialog

about = AboutDialog(parent = None,
                    image = ImageResource('ffnetui256x256'),
                    additions = ['<b>Feed-forward neural network for python</b>',
                                 '<a href=ffnet.sourceforge.net>http://ffnet.sourceforge.net</a>',
                                 '',
                                 'Copyright &copy; 2011-2015', '<b>Marek Wojciechowski</b>',
                                 '<a href=mailto:mwojc@p.lodz.pl>mwojc@p.lodz.pl</a>',
                                 '',
                                 ''])

if __name__ == "__main__":
    about.open()