"""Small, source-preserving HTML reader for the one-time content migration.

Offsets refer to Unicode characters in the UTF-8 snapshot, not byte offsets.
The parser never rewrites HTML. Original slices are the fidelity authority.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path("reports/baseline/phase-1")
MIGRATION = Path("content/migration")
VOID = set("area base br col embed hr img input link meta param source track wbr".split())
HEADINGS = {f"h{level}" for level in range(1, 7)}


def digest(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def route_file(path: str) -> Path:
    return Path("index.html") if path == "/" else Path(path.strip("/")) / "index.html"


@dataclass
class Node:
    tag: str
    attrs: dict
    start: int
    inner_start: int
    end: int = 0
    inner_end: int = 0
    parent: Node | None = field(default=None, repr=False)
    children: list[Node] = field(default_factory=list)

    def walk(self):
        for child in self.children:
            yield child
            yield from child.walk()

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get("class", "").split()

    def closest(self, predicate):
        node = self
        while node:
            if predicate(node):
                return node
            node = node.parent
        return None


class Document(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.line_starts = [0] + [match.end() for match in re.finditer("\n", source)]
        self.root = Node("document", {}, 0, 0, len(source), len(source))
        self.stack = [self.root]
        self.feed(source)
        self.close()
        if len(self.stack) != 1:
            raise ValueError(f"Unclosed HTML elements: {[node.tag for node in self.stack[1:]]}")

    def absolute_position(self):
        line, column = self.getpos()
        return self.line_starts[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.absolute_position()
        opening_end = start + len(self.get_starttag_text())
        node = Node(tag, dict(attrs), start, opening_end, parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag in VOID:
            node.end = node.inner_end = opening_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.end = node.inner_end = node.inner_start

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if len(self.stack) == 1 or self.stack[-1].tag != tag:
            raise ValueError(f"Unexpected closing {tag} at {self.getpos()}")
        node = self.stack.pop()
        node.inner_end = self.absolute_position()
        node.end = self.source.index(">", node.inner_end) + 1

    def nodes(self, predicate=lambda node: True):
        return [node for node in self.root.walk() if predicate(node)]

    def one(self, predicate):
        matches = self.nodes(predicate)
        if len(matches) != 1:
            raise ValueError(f"Expected one HTML node, found {len(matches)}")
        return matches[0]

    def raw(self, node: Node):
        return self.source[node.start:node.end]

    def text(self, node: Node):
        return plain_text(self.raw(node))


class TextReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.ignored = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.ignored += 1
        if tag in {"p", "div", "li", "br", "section", "article", *HEADINGS}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.ignored = max(0, self.ignored - 1)
        if tag in {"p", "div", "li", "section", "article", *HEADINGS}:
            self.parts.append(" ")

    def handle_data(self, value):
        if not self.ignored:
            self.parts.append(value)


def plain_text(source: str) -> str:
    reader = TextReader()
    reader.feed(source)
    return re.sub(r"\s+", " ", "".join(reader.parts)).strip()


def provenance(snapshot: str, source: str, start: int, end: int) -> dict:
    return {
        "snapshot": snapshot,
        "start": start,
        "end": end,
        "lineStart": source.count("\n", 0, start) + 1,
        "lineEnd": source.count("\n", 0, max(start, end - 1)) + 1,
        "sha256": digest(source[start:end]),
    }


def source_id(url: str) -> str:
    return "source-" + digest(url)[:16]
