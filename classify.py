#!/usr/bin/python2

SERIES_EPISODE_REGEX = '^([\s\w.]+)(?:\.| )S(\d+)\.E(\d+)'
IGNORE_REGEX = '\.(nfo|txt|bin|url|srt)$'

import argparse
import logging
import re
import os
import os.path
import subprocess
import sys

# FIXME: Avoid hard dependency on tvdb
import tvdb_api

from stat import S_ISDIR, S_ISREG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stderr))

error = logger.error
info = logger.info
debug = logger.debug
warning = logger.warning


class SeriesAnalyzer:
    """
    Analyze a folder tree and matches every file in it against the pattern for
    series episodes
    """

    regex = re.compile(SERIES_EPISODE_REGEX, re.IGNORECASE)
    ignore = re.compile(IGNORE_REGEX, re.IGNORECASE)
    episodes = []

    def __init__(self, folder):
        self.folder = folder

    def extract(self):
        self.walktree(self.folder, self.match_file)

    def walktree(self, root, callback):
        for f in os.listdir(root):
            pathname = os.path.join(root, f)

            try:
                mode = os.stat(pathname).st_mode
            except OSError:
                print("File vanished: %s" % pathname)
                continue

            if S_ISDIR(mode):
                debug("Exploring directory %s" % pathname)
                self.walktree(pathname, callback)
            elif S_ISREG(mode):
                debug("Found %s" % pathname)
                callback(pathname)
            else:
                debug("Ignoring %s", pathname)

    def match_file(self, name):
        path = os.path.basename(name)
        ign = self.ignore.search(path)

        if ign is not None:
            debug("Ignoring file type %s" % ign.group(1))
            return False

        match = self.regex.search(path)

        if match is None:
            debug("Unmatched %s" % path)
            return False

        series = match.group(1)
        season = int(match.group(2))
        episode = int(match.group(3))

        debug("Matched %s to %s" % (path, series))

        info = {'path': name, 'name': self.sanitize_name(name),
                'season': season, 'episode': episode}

        self.episodes.append(info)
        return True

    def sanitize_name(self, name):
        if '.' in name:
            name = ' '.join(name.split('.'))
        return name.capitalize()

    def get_infos(self):
        return self.episodes


class TVDBRenamer:
    """
    Renames and moves every media file from the given info tuple
    """

    T = tvdb_api.Tvdb()

    NAME_FORMAT = '%s.%s.%s - %s.%s'

    def __init__(self, info_tab, target_root):
        self.root = target_root
        self.infos = info_tab

    def process(self):
        for info in self.infos:
            show = self.T[info['name']]
            newname = show['seriesname']
            season = info['season']
            episode = info['episode']
            ext = info['path'][info['path'].rfind('.'):]
            ep_name = show[info['season']][info['episode']]

            final_name = self.NAME_FORMAT % (newname, season, episode, ep_name,
                                             ext)
            final_dir = os.path.join(self.root, newname, "Season " + season)
            final_path = final_dir + final_name

            os.makedirs(final_dir, exist_ok=True)
            os.rename(info['path'], final_path)


class SubtitlesFetcher:
    """
    Subtitles fetcher using subdl
    """

    def fetch_subtitles(self, path):
        subprocess.check_call(['subdl', path])


def tvdb_fetch(series, season, episode):
    t = tvdb_api.Tvdb()
    episode = t[series][season][episode]
    return episode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog=sys.argv[0])

    parser.add_argument('-o', '--output', type=str,
                        help="destination directory", required=True)
    parser.add_argument('-d', '--directory', type=str,
                        help='directory to be scanned', required=True)
    parser.add_argument('-t', '--tvdb', type=bool,
                        help='specify whether to use the tvdb api')
    parser.add_argument('-s', '--sub', type=bool,
                        help='fetches subtitles for every episode')

    info("Starting up classify...")

    args = parser.parse_args(sys.argv[1:])

    info("Walking through %s" % args.directory)

    paul_walker = SeriesAnalyzer(args.directory)

    paul_walker.extract()

    infos = paul_walker.get_infos()

    info("Done! Found %d episodes." % len(infos))

    if args.tvdb:
        info("Fetching additionnal informations from TVDB...")
        ren = TVDBRenamer(infos, args.output)
        ren.process()
        info("Done!")

    if args.sub:
        info("Fetching subtitles...")
        subber = SubtitlesFetcher()
        for ep in infos:
            debug("Looking up %s..." % ep['path'])
            subber.fetch_subtitles(ep['path'])
        info("Done!")
