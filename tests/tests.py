import os
import json
import unittest
import subprocess

class Testcf2toj(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['unzip', 'abc-3.zip', '-d', 'abc-3']) # with groups
        subprocess.run(['unzip', 'longestprimesum-4.zip', '-d', 'longestprimesum-4']) # with dependency
        # subprocess.run([]) # without groups
        # subprocess.run([]) # without points

    @classmethod
    def tearDownClass(cls):
        subprocess.run(['rm', '-r', 'abc-3'])
        subprocess.run(['rm', '-r', 'abc-3-toj'])
        subprocess.run(['rm', '-r', 'abc-3-toj.tar.xz'])
        subprocess.run(['rm', '-r', 'abc-3-toj-test'])

        subprocess.run(['rm', '-r', 'longestprimesum-4'])
        subprocess.run(['rm', '-r', 'longestprimesum-4-toj'])
        subprocess.run(['rm', '-r', 'longestprimesum-4-toj.tar.xz'])
        subprocess.run(['rm', '-r', 'longestprimesum-4-toj-test'])

        subprocess.run(['rm', 'cf2toj.py'])
        subprocess.run(['rm', 'function.py'])

    def test_with_groups(self):
        cf2toj_process = subprocess.run(['python3', 'cf2toj.py', 'abc-3', 'abc-3-toj'], capture_output=True)

        self.assertTrue(os.path.isfile('./abc-3-toj.tar.xz'))
        subprocess.run(['mkdir', 'abc-3-toj-test'])
        subprocess.run(['tar', 'xvf', 'abc-3-toj.tar.xz', '-C', 'abc-3-toj-test'])
        test_path = "abc-3-toj-test"

        self.assertTrue(os.path.isfile(f'{test_path}/conf.json'))
        self.assertTrue(os.path.isfile(f'{test_path}/http/cont.html'))

        with open(f'{test_path}/conf.json') as conf_file:
            conf = json.load(conf_file)
            self.assertEqual(int(conf['timelimit']), 1000)
            self.assertEqual(int(conf['memlimit']), 262144)
            self.assertEqual(len(conf['test']), 2)

            self.assertEqual(int(conf['test'][0]['weight']), 99)
            self.assertEqual(conf['test'][0]['data'], list(range(1, 23)))
            for i in conf['test'][0]['data']:
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.in"))
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.out"))

            self.assertEqual(int(conf['test'][1]['weight']), 1)
            self.assertEqual(conf['test'][1]['data'], list(range(23, 124)))
            for i in conf['test'][1]['data']:
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.in"))
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.out"))

    def test_with_dependency(self):
        cf2toj_process = subprocess.run(['python3', 'cf2toj.py', '--enable-dependency', 'longestprimesum-4', 'longestprimesum-4-toj'], capture_output=True)

        self.assertTrue(os.path.isfile('./longestprimesum-4-toj.tar.xz'))
        subprocess.run(['mkdir', 'longestprimesum-4-toj-test'])
        subprocess.run(['tar', 'xvf', 'longestprimesum-4-toj.tar.xz', '-C', 'longestprimesum-4-toj-test'])
        test_path = "longestprimesum-4-toj-test"

        self.assertTrue(os.path.isfile(f'{test_path}/conf.json'))
        self.assertTrue(os.path.isfile(f'{test_path}/http/cont.html'))

        with open(f'{test_path}/conf.json') as conf_file:
            conf = json.load(conf_file)
            self.assertEqual(int(conf['timelimit']), 1000)
            self.assertEqual(int(conf['memlimit']), 262144)
            self.assertEqual(len(conf['test']), 3)

            self.assertEqual(int(conf['test'][0]['weight']), 1)
            self.assertEqual(conf['test'][0]['data'], list(range(1, 2)))
            for i in conf['test'][0]['data']:
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.in"))
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.out"))

            self.assertEqual(int(conf['test'][1]['weight']), 50)
            self.assertEqual(conf['test'][1]['data'], list(range(2, 102)) + list(range(1, 2)))
            for i in conf['test'][1]['data']:
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.in"))
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.out"))

            self.assertEqual(int(conf['test'][2]['weight']), 49)
            self.assertEqual(conf['test'][2]['data'], list(range(102, 201)) + list(range(2, 102)))
            for i in conf['test'][2]['data']:
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.in"))
                self.assertTrue(os.path.isfile(f"{test_path}/res/testdata/{i}.out"))


if __name__ == '__main__':
    unittest.main()

# decompress testcase
# copy cf2toj.py & functions.py
# stdout = subprocess.run()
# decompress tar.xz
# open conf.json
# assert all json field
# assert testcase exist
# assert no background-color in problem-statement.css
#
# test `-c` && `--enable-dependency`
# --enable-dependency check conf.json
