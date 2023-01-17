""" This script runs the unittest of the EyeExperiment and EyeTrials classes
Hopefully, this will improve the code in both classes.
"""
import unittest as ut
import log.parseeyefile as pef
import log.eyeexperiment as exp
import pathlib


class TestExperimentFromFile(ut.TestCase):
    """Tests PsyExperiments"""

    file = (
        pathlib.Path(__file__).parents[1]
        / "data"
        / "reading"
        / "data"
        / "reading"
        / "dat"
        / "rea_11_000.asc"
    )

    def setUp(self):
        """Set up an EyeExperiment from a file inside the data"""
        pr = pef.parseEyeFile(self.file)
        self.exp = exp.EyeExperiment(pr.getEntries())

    def tearDown(self):
        self.exp = None

    def testCopy(self):
        """Copies an experiment and finds out whether it is a coppy"""
        copy = self.exp.copy()
        self.assertEqual(self.exp, copy)


if __name__ == "__main__":
    ut.main()
