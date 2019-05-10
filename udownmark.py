# Copyright (c) 2019 Paul Sokolovsky. MIT License.
import ure

class Markdown:

    def __init__(self, out):
        self.out = out
        self.block = ""
        self.typ = None

    def render_block(self, typ, block):
        if not block:
            return

        def tt(m):
            return "<tt>" + m.group(1).replace("<", "&lt;") + "</tt>"

        block = ure.sub("`(.+?)`", tt, block)
        block = ure.sub("\*\*(.+?)\*\*", "<b>\\1</b>", block)
        block = ure.sub("\*(.+?)\*", "<i>\\1</i>", block)
        block = ure.sub("~~(.+)~~", "<strike>\\1</strike>", block)
        block = ure.sub("!\[(.+?)\]\((.+?)\)", '<img src="\\2" alt="\\1">', block)
        block = ure.sub("\[(.+?)\]\((.+?)\)", '<a href="\\2">\\1</a>', block)

        if typ == "list":
            tag = "li"
        elif typ == "bquote":
            tag = "blockquote"
        else:
            tag = "p"

        self.out.write("<%s>\n" % tag)
        self.out.write(block)
        self.out.write("</%s>\n" % tag)

    def flush_block(self):
        self.render_block(self.typ, self.block)
        self.block = ""
        self.typ = None

    def render(self, lines):
        for l in lines:
            l_strip = l.rstrip()
            #print(l_strip)

            # Handle pre block content/end
            if self.typ == "```" or self.typ == "~~~":
                if l_strip == self.typ:
                    self.typ = None
                    self.out.write("</pre>\n")
                else:
                    self.out.write(l)
                continue

            # Handle pre block start
            if l.startswith("```") or l.startswith("~~~"):
                self.flush_block()
                self.typ = l[0:3]
                self.out.write("<pre>\n")
                continue

            # Empty line ends current block
            if not l_strip and self.block:
                self.flush_block()
                continue

            # Repeating empty lines are ignored - TODO
            if not l_strip:
                continue

            # Handle heading
            if l.startswith("#"):
                self.flush_block()
                level = 0
                while l.startswith("#"):
                    l = l[1:]
                    level += 1
                l = l.strip()
                self.out.write("<h%d>%s</h%d>\n" % (level, l, level))
                continue

            if l.startswith("> "):
                if self.typ != "bquote":
                    self.flush_block()
                self.typ = "bquote"
                l = l[2:]
            elif l.startswith("* "):
                self.flush_block()
                self.typ = "list"
                l = l[2:]

            if not self.typ:
                self.typ = "para"

            self.block += l

        # Render trailing block
        self.flush_block()
