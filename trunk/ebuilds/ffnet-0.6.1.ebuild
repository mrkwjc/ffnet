# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

inherit distutils python

DESCRIPTION="Feed-forward neural network for python"
HOMEPAGE="http://ffnet.soureceforge.net"
SRC_URI="mirror://sourceforge/${PN}/${P}.tar.gz"

SLOT="0"
KEYWORDS="~x86"
LICENSE="GPL-2"
IUSE="matplotlib"

DEPEND="virtual/python
	dev-python/networkx
	dev-python/numpy
	sci-libs/scipy
	matplotlib? ( dev-python/matplotlib )
	!dev-python/ffnet-svn"

pkg_setup() {
	einfo
	einfo "This package uses f2py and needs Fortran compiler"
	einfo "In general it should be detected automatically."
	einfo "For custom compiler set FC_VENDOR environment"
	einfo "variable:"
	einfo "export FC_VENDOR=gnu --> g77"
	einfo "export FC_VENDOR=gnu95 --> gfortran"
	einfo "export FC_VENDOR=intel --> ifort"
	einfo
}

src_compile() {
	distutils_src_compile \
		config_fc \
		--fcompiler=${FC_VENDOR} \
		|| die "compilation failed"
}

src_install() {
	distutils_src_install
	cp -r doc ${D}/usr/share/doc/${PF}
	cp -r examples ${D}/usr/share/doc/${PF}
}

pkg_postrm() {
	python_mod_cleanup
}

