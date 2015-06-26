#!/usr/bin/python2

import shutil
import tempfile
import unittest
import random
import os.path

from classify import SeriesAnalyzer, tvdb_fetch


def randchr():
    return chr(97 + random.randint(0, 51))  # Possible fix for uppercase


def randstr(size=40):
    s = ''
    for i in range(0, random.randint(1, size)):
        s = s + str(randchr())
    return s


class AnalyzerTest(unittest.TestCase):
    """
    Test case for the tree walker
    """

    FILE_NUM = random.randint(20, 50)
    FORMAT = '%s.S%02d.E%02d.mkv'

    REAL_EPISODE = 'Game.of.Thrones.S01E01.720p.HDTV.x264-CTU.mkv'

    real_files = []
    real_infos = {}

    def setUp(self):
        super(AnalyzerTest, self).setUp()
        self.create_tree()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def create_tree(self):
        self.dir = tempfile.mkdtemp(suffix='-test')

        for i in range(0, self.FILE_NUM):
            name = randstr()
            season = random.randint(1, 10)
            episode = random.randint(1, 24)
            real_name = self.FORMAT % (name, season, episode)
            path = os.path.join(self.dir, real_name)
            self.real_files.append(real_name)
            self.real_infos[name] = {'path': path, 'name': name,
                                     'season': int(season),
                                     'episode': int(episode)}
            fd = open(path, mode='w+')
            fd.close()

        self.analyzer = SeriesAnalyzer(self.dir)
        self.analyzer.extract()

    def test_walktree(self):
        for info in self.analyzer.get_infos():
            self.assertDictEqual(self.real_infos[info['name']], info)

    def test_walktree_real(self):
        tmpdir = tempfile.mkdtemp(suffix='classify.test')
        path = os.path.join(tmpdir, self.REAL_EPISODE)
        name = ' '.join(self.REAL_EPISODE.split('.')[:3])
        fd = open(path, "w+")
        fd.close()
        analyzer = SeriesAnalyzer(tmpdir)
        analyzer.extract()

        self.assertEquals(1, len(analyzer.get_infos()),
                          "Incorrectly matched 1 episode!")

        found_name = analyzer.get_infos()[0]['name']
        self.assertEquals(name, found_name,
                          "Incorrectly matched episode name: %s!" % found_name)

    def test_tvdb(self):
        episodes = [("House M.D.", 1, 12)]
        names = ["Sports Medicine"]
        for i in range(0, len(episodes)):
            info = episodes[i]
            tvdb = tvdb_fetch(info[0], info[1], info[2])
            self.assertEquals(tvdb['episodename'], names[i])

if __name__ == '__main__':
    unittest.main()
