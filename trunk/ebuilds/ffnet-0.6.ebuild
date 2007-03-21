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

# set environment variable F2PY_FC with proper f2py compiler name
# or gnu compilers will be used
if [ ${F2PY_FC} ]; then
	FCOMPILER="--fcompiler=${F2PY_FC}"
fi
	

src_compile() {
	distutils_src_compile \
		config_fc \
		${FCOMPILER} \
		--opt="${CFLAGS}" \
		|| die "compilation failed"
}

src_install() {
	distutils_src_install

	#dodoc README
    cp -r doc ${D}/usr/share/doc/${PF}
	cp -r examples ${D}/usr/share/doc/${PF}
}
