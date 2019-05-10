import glob
from subprocess import check_call

from udownmark import Markdown


for f in glob.glob("tests/*.md"):
    print(f)
    with open(f) as inp, open(f + ".out", "w") as outp:
        m = Markdown(outp)
        m.render(inp)
    check_call("diff -u %s %s" % (f.replace(".md", ".html"), f + ".out"), shell=True)
