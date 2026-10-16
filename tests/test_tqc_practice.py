"""Run: python3 -m unittest discover -s tests -p 'test_tqc_practice.py' -v"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tqc_grade', ROOT / 'tqc_practice/grade.py')
grader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grader)


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / 'answer.py'
        self.bank = grader.load_bank()

    def write(self, text):
        self.source.write_text(text, encoding='utf-8')
        return self.source

    def test_all_16_reference_programs_pass_all_61_cases(self):
        self.assertEqual(len(self.bank), 16)
        self.assertEqual(sum(len(q['cases']) for q in self.bank.values()), 61)
        for qid, question in self.bank.items():
            with self.subTest(question=qid):
                if qid == 'Q510':
                    source = self.write(
                        'def compute(num):\n'
                        '    a, b = 0, 1\n'
                        '    for _ in range(num):\n'
                        '        print(a, end=" ")\n'
                        '        a, b = b, a + b\n'
                        'compute(int(input()))\n')
                else:
                    source = ROOT / 'TQC-PY/vip' / ('PYD' + qid[1:] + '.py')
                results = grader.evaluate(source, question)
                self.assertTrue(all(r['status'] == 'OK' for r in results), results)

    def test_format_comparison(self):
        self.assertEqual(grader.normalize('abc  \r\n'), 'abc')
        self.assertNotEqual(grader.normalize(' *'), grader.normalize('*'))
        self.assertNotEqual(grader.normalize('a  b'), grader.normalize('a b'))
        self.assertNotEqual(grader.normalize('a\n\nb'), grader.normalize('a\nb'))
        self.assertNotEqual(grader.normalize('a \n', True), grader.normalize('a\n', True))

    def test_wrong_answer_and_strict_mode(self):
        question = {'cases': [{'name': 'format', 'stdin': '', 'stdout': '1\n'}]}
        self.write('print("1 ")')
        self.assertEqual(grader.evaluate(self.source, question)[0]['status'], 'OK')
        self.assertEqual(grader.evaluate(self.source, question, strict=True)[0]['status'], 'WRONG')
        self.write('print(2)')
        self.assertEqual(grader.evaluate(self.source, question)[0]['status'], 'WRONG')

    def test_syntax_and_runtime_errors(self):
        for source in ['if :', '1 / 0', 'input()']:
            with self.subTest(source=source):
                result = grader.execute(self.write(source), {'stdin': ''})
                self.assertEqual(result['status'], 'ERROR')
                self.assertTrue(result['stderr'])

    def test_infinite_loop_timeout(self):
        result = grader.execute(self.write('while True: pass'), {}, timeout=0.15)
        self.assertEqual(result['status'], 'TIMEOUT')

    def test_excessive_output(self):
        result = grader.execute(self.write('while True: print("x" * 4096)'), {})
        self.assertEqual(result['status'], 'OUTPUT_LIMIT')
        self.assertLessEqual(len(result['stdout']), grader.OUTPUT_LIMIT)

    def test_906_requires_writing_back_and_resets_fixture(self):
        source = self.write(
            'name, old, new = input(), input(), input()\n'
            'with open(name, encoding="utf-8") as f: text = f.read()\n'
            'print("=== Before the replacement")\nprint(text)\n'
            'print("=== After the replacement")\nprint(text.replace(old, new))\n')
        results = grader.evaluate(source, self.bank['Q906'])
        self.assertEqual(results[0]['status'], 'FILE')
        self.assertEqual(results[2]['status'], 'OK')  # No match: original is already correct.
        correct = ROOT / 'TQC-PY/vip/PYD906.py'
        for _ in range(2):
            self.assertTrue(all(r['status'] == 'OK'
                                for r in grader.evaluate(correct, self.bank['Q906'])))
        self.assertFalse((self.source.parent / 'read.txt').exists())

    def test_function_requirement(self):
        result = grader.evaluate(self.write('print(int(input()) * int(input()))'), self.bank['Q502'])
        self.assertEqual(result[0]['status'], 'FUNCTION')

    def test_question_ids_and_path_rejection(self):
        for value in ['Q110', '110', 'q110.py', ' Q110 ']:
            self.assertEqual(grader.question_id(value), 'Q110')
        for value in ['../Q110', '/tmp/a.py', 'Q110;ls', '1100']:
            with self.assertRaises(ValueError):
                grader.question_id(value)

    def test_interactive_commands_from_other_directory(self):
        with ZipFile(ROOT / 'tqc_practice.zip') as archive:
            archive.extractall(self.tmp.name)
        result = subprocess.run(
            [sys.executable, str(Path(self.tmp.name) / 'tqc_practice/grade.py')],
            input='list\nshow Q110\nQ999\n../bad\nQ110\nexit\n',
            text=True, encoding='utf-8', capture_output=True, cwd=self.tmp.name, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('面積公式', result.stdout)
        self.assertIn('沒有這個題號', result.stdout)
        self.assertIn('題號格式不正確', result.stdout)
        self.assertIn('尚未通過', result.stdout)
        self.assertIn('預期：', result.stdout)

    def test_packaged_student_files_are_blank(self):
        with ZipFile(ROOT / 'tqc_practice.zip') as archive:
            for qid in self.bank:
                name = 'tqc_practice/questions/' + qid
                text = archive.read(name + '.py').decode('utf-8')
                self.assertTrue(all(not line.strip() or line.startswith('#')
                                    for line in text.splitlines()))
                self.assertIn(name + '.md', archive.namelist())


if __name__ == '__main__':
    unittest.main()
