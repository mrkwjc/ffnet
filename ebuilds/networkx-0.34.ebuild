# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit distutils python

DESCRIPTION="NetworkX is a python graph library"
HOMEPAGE="https://networkx.lanl.gov/"
SRC_URI="http://networkx.lanl.gov/download/${P}.tar.gz"

SLOT="0"
KEYWORDS="~x86"
LICENSE="LGPL-2"
IUSE="matplotlib graphviz"

DEPEND="virtual/python
	dev-python/setuptools
	matplotlib? ( dev-python/matplotlib )
	graphviz? ( >=media-gfx/pydot-0.9.10 )"


src_install() {
	distutils_src_install
	distutils_python_version

	insinto /usr/lib/python${PYVER}/site-packages
	echo "${P}-py${PYVER}.egg" > "${P}-py${PYVER}.pth"
	doins "${P}-py${PYVER}.pth"

	dodoc doc/*.txt
	cp -r doc/test.py doc/data doc/examples ${D}/usr/share/doc/${PF}
}
