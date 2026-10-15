#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""extract.py -- regenerate this repository's example files from the upstream specs.

The data files here are adaptations of two CC-BY-SA 4.0 specifications (see
README.md and LICENSE); this script is the whole of the adaptation, so that
anyone can check it and redo it.

    python3 tools/extract.py --commonmark ../commonmark-spec --gfm ../cmark-gfm
    python3 tools/extract.py --commonmark ... --gfm ... --check   # verify only

--commonmark is a checkout of https://github.com/commonmark/commonmark-spec and
--gfm a checkout of https://github.com/github/cmark-gfm, each at the commit
pinned in SOURCES below.  The script refuses to run when an input's SHA-256 is
not the pinned one: moving to a new spec version is an edit to SOURCES, never a
silent change of input.  Python 3.8+, standard library only, no network.

Outputs:

  commonmark/<version>/spec.json
      Every example of the CommonMark spec, byte-for-byte what upstream's
      `python3 test/spec_tests.py --dump-tests < spec.txt` writes -- the same
      file upstream publishes as https://spec.commonmark.org/<version>/spec.json.
      Fields: markdown, html, example, start_line, end_line, section.

  gfm/<version>/extensions.json
      Only the GFM spec's extension examples (tables, strikethrough, extended
      autolinks, the tag filter, task lists).  Its core examples are omitted:
      the GFM spec is based on an older CommonMark, and the CommonMark file
      above is the authority for the core.  Same fields, plus `extensions` --
      the marker on the example's fence -- and `upstream_disabled`, true for
      the two task-list examples upstream fences as `example disabled` (its
      own test runner skips them; the spec text still specifies them).

  SOURCES.json
      Provenance: upstream repository, tag, commit, file, SHA-256, and the
      example counts written.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SOURCES = {
    'commonmark': {
        'name': 'CommonMark Spec',
        'version': '0.31.2',
        'repository': 'https://github.com/commonmark/commonmark-spec',
        'tag': '0.31.2',
        'commit': '9103e341a973013013bb1a80e13567007c5cef6f',
        'path': 'spec.txt',
        'sha256': '257c41ad946f7a1414a499aca402a1aa8fdac3678532266611348c1cf54f4b80',
        'author': 'John MacFarlane',
        'license': 'CC-BY-SA-4.0',
    },
    'gfm': {
        'name': 'GitHub Flavored Markdown Spec',
        'version': '0.29-gfm',
        'repository': 'https://github.com/github/cmark-gfm',
        'tag': '0.29.0.gfm.13',
        'commit': '587a12bb54d95ac37241377e6ddc93ea0e45439b',
        'path': 'test/spec.txt',
        'sha256': '7d8e5814befec287ac116786d81ff14e0adc9b13295b4494649e995408fd871c',
        'author': 'GitHub (github/cmark-gfm); based on the CommonMark Spec by John MacFarlane',
        'license': 'CC-BY-SA-4.0',
    },
}

FENCE = '`' * 32
HEADER_RE = re.compile('#+ ')
# A task-list example is fenced `example disabled`; its section names it.
DISABLED_SECTIONS = {'Task list items (extension)': 'tasklist'}


def get_examples(path):
    """Every example in a spec file.

    The same state machine as upstream's test/spec_tests.py get_tests() --
    both repositories' copies -- plus the fence's marker words: an example
    fence is FENCE + ' example' + optional markers, and `→` stands for a tab.
    """
    examples = []
    state = 0  # 0 prose, 1 markdown, 2 html
    markdown, html, markers = [], [], []
    start_line = number = 0
    section = ''
    with open(path, 'r', encoding='utf-8', newline='\n') as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if stripped.startswith(FENCE + ' example'):
                state = 1
                markers = stripped[len(FENCE + ' example'):].split()
            elif state == 2 and stripped == FENCE:
                state = 0
                number += 1
                examples.append({
                    'markdown': ''.join(markdown).replace('→', '\t'),
                    'html': ''.join(html).replace('→', '\t'),
                    'example': number,
                    'start_line': start_line,
                    'end_line': line_number,
                    'section': section,
                    'markers': markers,
                })
                markdown, html, start_line = [], [], 0
            elif stripped == '.':
                state = 2
            elif state == 1:
                if start_line == 0:
                    start_line = line_number - 1
                markdown.append(line)
            elif state == 2:
                html.append(line)
            elif state == 0 and HEADER_RE.match(line):
                section = HEADER_RE.sub('', line).strip()
    return examples


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_input(root, key):
    src = SOURCES[key]
    path = Path(root) / src['path']
    if not path.is_file():
        sys.exit(f'error: {path} not found (expected a checkout of {src["repository"]})')
    digest = sha256(path)
    if digest != src['sha256']:
        sys.exit(f'error: {path} has SHA-256 {digest}, but SOURCES pins '
                 f'{src["sha256"]} ({src["repository"]} at {src["tag"]}).\n'
                 f'       check out commit {src["commit"]}, or update SOURCES '
                 f'deliberately to move to another version.')
    return path


def commonmark_json(path):
    tests = [{k: v for k, v in ex.items() if k != 'markers'} for ex in get_examples(path)]
    # upstream: out(json.dumps(tests, ensure_ascii=False, indent=2)), no newline
    return json.dumps(tests, ensure_ascii=False, indent=2)


def gfm_json(path):
    out = []
    for ex in get_examples(path):
        markers = ex.pop('markers')
        if not markers:
            continue
        disabled = markers == ['disabled']
        if disabled:
            if ex['section'] not in DISABLED_SECTIONS:
                sys.exit(f'error: a disabled example outside a known section: '
                         f'#{ex["example"]} in {ex["section"]!r}')
            markers = [DISABLED_SECTIONS[ex['section']]]
        ex['extensions'] = markers
        ex['upstream_disabled'] = disabled
        out.append(ex)
    return json.dumps(out, ensure_ascii=False, indent=2) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--commonmark', required=True, help='commonmark/commonmark-spec checkout')
    ap.add_argument('--gfm', required=True, help='github/cmark-gfm checkout')
    ap.add_argument('--check', action='store_true',
                    help='verify the committed files instead of writing them')
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    cm_in = checked_input(args.commonmark, 'commonmark')
    gfm_in = checked_input(args.gfm, 'gfm')
    cm_text = commonmark_json(cm_in)
    gfm_text = gfm_json(gfm_in)

    cm_out = root / 'commonmark' / SOURCES['commonmark']['version'] / 'spec.json'
    gfm_out = root / 'gfm' / SOURCES['gfm']['version'] / 'extensions.json'
    counts = {
        str(cm_out.relative_to(root)): len(json.loads(cm_text)),
        str(gfm_out.relative_to(root)): len(json.loads(gfm_text)),
    }
    sources_text = json.dumps({
        'sources': SOURCES,
        'outputs': {
            str(cm_out.relative_to(root)): {'from': 'commonmark', 'examples': counts[str(cm_out.relative_to(root))]},
            str(gfm_out.relative_to(root)): {'from': 'gfm', 'examples': counts[str(gfm_out.relative_to(root))]},
        },
    }, indent=2) + '\n'

    files = {cm_out: cm_text, gfm_out: gfm_text, root / 'SOURCES.json': sources_text}
    if args.check:
        stale = [str(p.relative_to(root)) for p, text in files.items()
                 if not p.is_file() or p.read_text(encoding='utf-8') != text]
        if stale:
            sys.exit('error: out of date: ' + ', '.join(stale))
        print('ok:', ', '.join(f'{k} ({v} examples)' for k, v in counts.items()))
        return
    for p, text in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')
    print('wrote:', ', '.join(f'{k} ({v} examples)' for k, v in counts.items()))


if __name__ == '__main__':
    main()
