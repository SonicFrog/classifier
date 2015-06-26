# Copyright 1999-2013 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $

EAPI=5

inherit git-2

DESCRIPTION="A python script to sort automatically your TV series"
HOMEPAGE="https://github.com/SonicFrog/classifier"
EGIT_REPO_URI="https://github.com/SonicFrog/classifier.git"
SLOT="0"
LICENSE="GPL-2.0"

IUSE="subtitles tvdb"

RDEPEND="dev-lang/python:2
		 tvdb? (dev-python/tvdb_api)
		 subtitles? (media-video/subdl)"

DEPEND="${RDEPEND}"

KEYWORDS="~amd64 ~arm ~x86"

PYTHON_COMPAT=( python2_6 python2_7)

src_install() {
	default
}
