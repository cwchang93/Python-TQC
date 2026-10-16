#!/usr/bin/env python3
"""Offline classroom practice grader. Python 3.9+, standard library only."""
import argparse
import ast
import difflib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parent
OUTPUT_LIMIT = 65536
TIMEOUT = 3


def load_bank():
    return json.loads((ROOT / 'data' / 'cases.json').read_text(encoding='utf-8'))


def question_id(value):
    value = value.strip().upper()
    if value.endswith('.PY'):
        value = value[:-3]
    if re.fullmatch(r'(Q)?\d{3}', value):
        return 'Q' + value[-3:]
    raise ValueError('題號格式不正確，請輸入 Q110 或 110。')


def normalize(text, strict=False):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    if strict:
        return text
    return '\n'.join(line.rstrip(' \t') for line in text.split('\n')).rstrip('\n')


def execute(source, case, timeout=TIMEOUT):
    """Use a fresh working directory per case; this is not a security sandbox."""
    with tempfile.TemporaryDirectory(prefix='tqc_practice_') as directory:
        work = Path(directory)
        submission = work / 'submission.py'
        submission.write_bytes(Path(source).read_bytes())
        for name, content in case.get('files', {}).items():
            (work / name).write_text(content, encoding='utf-8')
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
        process = subprocess.Popen(
            [sys.executable, '-B', str(submission)], cwd=work, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        buffers = {'stdout': bytearray(), 'stderr': bytearray()}
        exceeded = threading.Event()

        def drain(stream, name):
            try:
                while True:
                    chunk = stream.read(4096)
                    if not chunk:
                        break
                    remaining = OUTPUT_LIMIT - len(buffers[name])
                    buffers[name].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        exceeded.set()
                        process.kill()
                        break
            finally:
                stream.close()

        readers = [threading.Thread(target=drain, args=(stream, name), daemon=True)
                   for stream, name in [(process.stdout, 'stdout'), (process.stderr, 'stderr')]]
        for reader in readers:
            reader.start()
        timed_out = False
        try:
            try:
                process.stdin.write(case.get('stdin', '').encode('utf-8'))
                process.stdin.close()
            except BrokenPipeError:
                pass
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait()
        finally:
            for reader in readers:
                reader.join(timeout=1)
        result = {key: bytes(value).decode('utf-8', errors='replace')
                  for key, value in buffers.items()}
        result['files'] = {}
        for name in case.get('expected_files', {}):
            target = work / name
            if target.is_file():
                with target.open('rb') as handle:
                    raw = handle.read(OUTPUT_LIMIT + 1)
                if len(raw) > OUTPUT_LIMIT:
                    exceeded.set()
                result['files'][name] = raw.decode('utf-8', errors='replace')
            else:
                result['files'][name] = None
        result['status'] = ('OUTPUT_LIMIT' if exceeded.is_set() else
                            'TIMEOUT' if timed_out else
                            'ERROR' if process.returncode else 'OK')
        return result


def evaluate(source, question, strict=False, timeout=TIMEOUT):
    required = question.get('function')
    if required:
        try:
            tree = ast.parse(Path(source).read_text(encoding='utf-8-sig'))
        except (SyntaxError, UnicodeError):
            tree = None  # Let Python report the actual error below.
        if tree is not None and not any(
            isinstance(node, ast.FunctionDef) and node.name == 'compute'
            and len(node.args.posonlyargs + node.args.args) == required
            for node in tree.body
        ):
            return [{'status': 'FUNCTION', 'name': '函式規格',
                     'detail': '請定義 compute()，接受 %d 個參數。' % required}]
    results = []
    for case in question['cases']:
        result = execute(source, case, timeout)
        result.update(name=case['name'], case=case)
        if result['status'] == 'OK':
            if normalize(result['stdout'], strict) != normalize(case['stdout'], strict):
                result['status'] = 'WRONG'
            else:
                for name, expected in case.get('expected_files', {}).items():
                    actual = result['files'][name]
                    # File contents are part of the answer; preserve spaces and newlines.
                    if actual is None or normalize(actual, True) != normalize(expected, True):
                        result.update(status='FILE', file_name=name)
                        break
        results.append(result)
    return results


def show_difference(expected, actual):
    # repr exposes invisible whitespace; truncate only the display, not the comparison.
    print('  預期：', repr(expected[:1200]))
    print('  實際：', repr(actual[:1200]))
    diff = list(difflib.unified_diff(expected.splitlines(), actual.splitlines(),
                                   fromfile='預期', tofile='實際', lineterm=''))
    for line in diff[:24]:
        print('  ' + line[:200])


def grade(qid, bank, strict=False):
    if qid not in bank:
        print('沒有這個題號。輸入 list 查看 16 題。')
        return False
    source = ROOT / 'questions' / (qid + '.py')
    if not source.is_file():
        print('找不到作答檔：' + str(source))
        return False
    question = bank[qid]
    print('\n%s %s（%s模式）' % (qid, question['title'], '嚴格' if strict else '練習'))
    results = evaluate(source, question, strict)
    labels = {'OK': '通過', 'WRONG': '輸出不符', 'ERROR': '執行錯誤',
              'TIMEOUT': '執行逾時（檢查迴圈是否有結束）',
              'OUTPUT_LIMIT': '輸出過多（檢查是否重複印出）',
              'FILE': '寫入檔案內容不符', 'FUNCTION': '函式規格不符'}
    for index, result in enumerate(results, 1):
        print('  [%s] 測資 %d：%s — %s' % (
            'PASS' if result['status'] == 'OK' else 'FAIL', index,
            result['name'], labels[result['status']]))
    passed = sum(item['status'] == 'OK' for item in results)
    success = passed == len(results)
    print('結果：%s｜%d/%d 通過｜練習分數 %d/100' % (
        '全部通過！' if success else '尚未通過', passed, len(results),
        round(100 * passed / len(results))))
    failed = next((item for item in results if item['status'] != 'OK'), None)
    if failed:
        print('\n第一個未通過項目的說明：')
        case = failed.get('case', {})
        if case:
            print('  測試輸入：', repr(case.get('stdin', '')))
            for name, content in case.get('files', {}).items():
                print('  測試檔案 %s：%r' % (name, content))
        if failed['status'] == 'WRONG':
            show_difference(case['stdout'], failed['stdout'])
        elif failed['status'] == 'FILE':
            name = failed['file_name']
            print('  檔案：' + name)
            show_difference(case['expected_files'][name],
                            failed['files'][name] if failed['files'][name] is not None else '(檔案不存在)')
        elif failed['status'] == 'ERROR':
            print(failed['stderr'][-3000:])
        elif failed['status'] == 'FUNCTION':
            print('  ' + failed['detail'])
        print('修改後存檔，再輸入同一題號重測。')
    return success


def list_questions(bank):
    for qid, question in bank.items():
        print('  %s  %s' % (qid, question['title']))


def main():
    parser = argparse.ArgumentParser(description='TQC VIP 離線練習評分（非官方）')
    parser.add_argument('question', nargs='?', help='例如 Q110、110，或 all')
    parser.add_argument('--strict', action='store_true', help='連行尾空白、最後換行也比對')
    args = parser.parse_args()
    bank = load_bank()
    if args.question:
        if args.question.lower() == 'all':
            outcomes = [grade(qid, bank, args.strict) for qid in bank]
            return 0 if all(outcomes) else 1
        try:
            return 0 if grade(question_id(args.question), bank, args.strict) else 1
        except ValueError as error:
            print(error)
            return 2
    print('TQC VIP 離線練習｜16 題｜非官方評分器')
    print('先編輯 questions/Qxxx.py 並存檔，再回來輸入題號。')
    print('指令：Q110 / list / show Q110（題目）/ all / exit')
    list_questions(bank)
    while True:
        try:
            command = input('\n請輸入題號 > ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n已結束。')
            return 0
        if command.lower() in ('exit', 'quit', 'q'):
            return 0
        if not command:
            continue
        if command.lower() == 'list':
            list_questions(bank)
        elif command.lower() == 'all':
            for qid in bank:
                grade(qid, bank, args.strict)
        else:
            try:
                if command.lower().startswith('show '):
                    qid = question_id(command[5:])
                    if qid not in bank:
                        print('沒有這個題號。')
                    else:
                        print((ROOT / 'questions' / (qid + '.md')).read_text(encoding='utf-8'))
                else:
                    grade(question_id(command), bank, args.strict)
            except ValueError as error:
                print(error)


if __name__ == '__main__':
    sys.exit(main())
