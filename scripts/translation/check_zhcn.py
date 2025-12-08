import argparse
import json
import re
from pathlib import Path

# Load whitelist
BASE_DIR = Path(__file__).resolve().parent.parent.parent
WHITELIST_PATH = BASE_DIR / 'scripts' / 'translation' / 'terminology_whitelist.txt'

if WHITELIST_PATH.exists():
    WHITELIST = set(w.strip() for w in WHITELIST_PATH.read_text(encoding='utf-8').splitlines() if w.strip())
else:
    WHITELIST = set()

RE_WORD = re.compile(r"[A-Za-z][A-Za-z0-9\-_/\.]{2,}")


def is_code_block(line):
    return line.strip().startswith('```')


def scan_file(path: Path, counterpart: Path):
    result = {
        'english': str(path),
        'chinese': str(counterpart) if counterpart else None,
        'status': 'ok',
        'missing': False,
        'outdated': False,
        'untranslated_snippets': [],
        'structure_diff': {},
    }

    if not counterpart or not counterpart.exists():
        result['status'] = 'missing'
        result['missing'] = True
        return result

    eng = path.read_text(encoding='utf-8', errors='ignore').splitlines()
    zh = counterpart.read_text(encoding='utf-8', errors='ignore').splitlines()

    # Structure compare
    def count_struct(lines, token):
        return sum(1 for l in lines if l.strip().startswith(token))

    struct = {
        'heading': (count_struct(eng, '#'), count_struct(zh, '#')),
        'codeblock': (sum(1 for l in eng if l.strip().startswith('```')), sum(1 for l in zh if l.strip().startswith('```'))),
        'tables': (sum(1 for l in eng if '|' in l), sum(1 for l in zh if '|' in l)),
    }
    diff_struct = {k: v for k, v in struct.items() if v[0] != v[1]}
    if diff_struct:
        result['outdated'] = True
        result['structure_diff'] = diff_struct

    # Length heuristic
    if abs(len('\n'.join(eng)) - len('\n'.join(zh))) / max(len('\n'.join(eng)), 1) > 0.1:
        result['outdated'] = True

    # Scan untranslated English (outside code fences, and not in whitelist)
    in_code = False
    for idx, line in enumerate(zh, 1):
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        # skip if link-only
        if re.fullmatch(r"\[.*\]\(.*\)", line.strip()):
            continue
        for m in RE_WORD.finditer(line):
            token = m.group(0)
            if token in WHITELIST:
                continue
            # If token contains mixed case or looks like sentence word, flag
            if any(c.islower() for c in token) and any(c.isupper() for c in token):
                continue
            # words like 'the' should not trigger
            if token.lower() in {'the','and','with','for','of','in','on','at','to','is','are','be','an','a','or','by','as','from','this','that','these','those'}:
                continue
            result['untranslated_snippets'].append({'line': idx, 'token': token, 'context': line.strip()[:160]})
            break

    if result['untranslated_snippets']:
        result['status'] = 'outdated'
    return result


def main():
    parser = argparse.ArgumentParser(description='Check zh-cn translations')
    parser.add_argument('--output', default='scripts/translation/check_report.json', help='Path to write JSON report')
    args = parser.parse_args()

    report = []
    base = Path('.')
    english_files = [p for p in base.rglob('*.md') if not p.name.endswith('_zh-cn.md') and '.git' not in p.parts]

    for eng in sorted(english_files):
        zh = eng.with_name(eng.stem + '_zh-cn.md')
        result = scan_file(eng, zh if zh.exists() else None)
        report.append(result)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    missing = sum(1 for r in report if r['missing'])
    outdated = sum(1 for r in report if r['status']=='outdated')
    ok = sum(1 for r in report if r['status']=='ok')
    print(f"Total: {len(report)}, OK: {ok}, Outdated: {outdated}, Missing: {missing}")
    if outdated:
        print('Outdated files sample:')
        for r in report[:10]:
            if r['status']=='outdated':
                print('-', r['english'])

if __name__ == '__main__':
    main()
