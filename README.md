# commonmark-spec

The CommonMark and GitHub Flavored Markdown specification examples, as JSON,
for testing [Turmeric](https://github.com/turmeric-lang/turmeric)'s Markdown
library (`tur/markdown`; see
[`docs/upcoming/markdown-library-plan.md`](https://github.com/turmeric-lang/turmeric/blob/main/docs/upcoming/markdown-library-plan.md)).

The examples are licensed under CC-BY-SA 4.0. They live in their own
repository so that the share-alike licence stays separate from the MIT-licensed
Turmeric source.

## Contents

| File | What it holds |
|---|---|
| `commonmark/0.31.2/spec.json` | All **652** examples of the [CommonMark Spec](https://spec.commonmark.org/0.31.2/) 0.31.2. Byte-for-byte what upstream's `test/spec_tests.py --dump-tests` produces, which is the file upstream publishes as `https://spec.commonmark.org/0.31.2/spec.json`. |
| `gfm/0.29-gfm/extensions.json` | The **24** extension examples of the [GitHub Flavored Markdown Spec](https://github.github.com/gfm/) 0.29-gfm: 8 tables, 2 strikethrough, 11 extended autolinks, 1 tag filter, 2 task lists. |
| `SOURCES.json` | Provenance: the upstream repository, tag, commit, file and SHA-256 behind each output, and the number of examples written. |
| `tools/extract.py` | The script that produces the three files above from the pinned upstream sources. |

Each example is an object with these fields:

- `markdown`: the input, with tabs as real tab characters
- `html`: the expected output
- `example`: the example number in its spec
- `start_line` and `end_line`: where the example sits in that spec's `spec.txt`
- `section`: the heading it appears under

`extensions.json` adds two fields:

- `extensions`: the extension the example exercises (`table`, `strikethrough`,
  `autolink`, `tagfilter` or `tasklist`).
- `upstream_disabled`: true for the two task-list examples, which upstream
  marks `example disabled` and which its own test runner skips. The spec still
  defines their output, and GitHub's renderer produces it once the HTML is
  normalised.

The GFM spec's core examples are left out on purpose. The GFM spec is built on
CommonMark 0.29, and `commonmark/0.31.2/spec.json` is the authority for the
core syntax.

### Comparing output

The specs compare HTML after normalising it: attribute order, and whitespace
between block tags. The reference implementation is upstream's
`test/normalize.py`, which is BSD-2-Clause and not included here. A consumer
should apply the same normalisation before comparing.

## Using it from Turmeric

Clone it next to the `turmeric` checkout, the same way as `turmeric-spices`:

```sh
git clone https://github.com/turmeric-lang/commonmark-spec ../commonmark-spec
```

Turmeric's spec runner reads it from `../commonmark-spec/`, and skips with a
message when it's absent. CI checks it out at a commit pinned in the
`turmeric` repository, so a change here only reaches Turmeric's tests when that
pin moves.

## Regenerating

```sh
git clone --depth 1 --branch 0.31.2       https://github.com/commonmark/commonmark-spec /tmp/commonmark-spec
git clone --depth 1 --branch 0.29.0.gfm.13 https://github.com/github/cmark-gfm        /tmp/cmark-gfm
python3 tools/extract.py --commonmark /tmp/commonmark-spec --gfm /tmp/cmark-gfm           # write
python3 tools/extract.py --commonmark /tmp/commonmark-spec --gfm /tmp/cmark-gfm --check   # verify
```

The script refuses to run if an input `spec.txt` doesn't match its pinned
SHA-256. Moving to a new spec version means editing `SOURCES` in
`tools/extract.py` (tag, commit, digest, version) and committing the
regenerated files together.

## Attribution and licence

- **CommonMark Spec** 0.31.2, copyright (C) 2014-16 John MacFarlane.
  <https://spec.commonmark.org/0.31.2/>, from
  <https://github.com/commonmark/commonmark-spec> at tag `0.31.2`.
- **GitHub Flavored Markdown Spec** 0.29-gfm, by GitHub, based on the
  CommonMark Spec. <https://github.github.com/gfm/>, from
  <https://github.com/github/cmark-gfm> at tag `0.29.0.gfm.13`.

Both specifications are licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/)
licence.

**Changes made:** only the examples were extracted from each specification's
`spec.txt`, as JSON objects. Each example's input and expected output are
unchanged, except that `→` (the spec's visible-tab notation) is written as a
real tab, as upstream's own tooling does. The GFM file keeps only the extension
examples and records which extension each one exercises. The prose of the
specifications is not included.

The JSON data files (`commonmark/`, `gfm/`, `SOURCES.json`) are adaptations of
those specifications and are released under the same licence, CC-BY-SA 4.0. Its
full text is in [`LICENSE`](LICENSE). The extraction script in `tools/` is
original work, licensed under the MIT License: see
[`tools/LICENSE.md`](tools/LICENSE.md).
