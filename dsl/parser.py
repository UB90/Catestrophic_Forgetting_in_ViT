from lark import Lark, Transformer

GRAMMAR = r"""
    start: instruction+

    ?instruction: count | detail | verify | resize | convert | rename

    count: "count" STRING
    detail: "detail" STRING "to" STRING
    verify: "verify" STRING
    resize: "resize" STRING "to" resolution ("," resolution)* "in" STRING
    convert: "convert" STRING "to" MODE "in" STRING
    rename: "rename" STRING "to" STRING "as" FORMAT

    resolution: INT "x" INT

    FORMAT: "png" | "jpg" | "jpeg" | "bmp" | "tiff"
    MODE: "rgb" | "grayscale" | "l" | "rgba"

    %import common.ESCAPED_STRING -> STRING
    %import common.INT
    %import common.WS
    
    COMMENT: /#[^\n]*/
    
    %ignore WS
    %ignore COMMENT
"""

class ScriptTransformer(Transformer):
    def start(self, items):
        return items

    def count(self, items):
        return {"action": "count", "dataset": items[0].value[1:-1]}

    def detail(self, items):
        return {"action": "detail", "dataset": items[0].value[1:-1], "output": items[1].value[1:-1]}

    def verify(self, items):
        return {"action": "verify", "dataset": items[0].value[1:-1]}

    def resize(self, items):
        dataset = items[0].value[1:-1]
        outdir = items[-1].value[1:-1]
        resolutions = items[1:-1]
        return {"action": "resize", "dataset": dataset, "resolutions": resolutions, "outdir": outdir}

    def resolution(self, items):
        return (int(items[0].value), int(items[1].value))

    def convert(self, items):
        return {"action": "convert", "dataset": items[0].value[1:-1], "format": str(items[1]), "outdir": items[2].value[1:-1]}

    def rename(self, items):
        return {"action": "rename", "dataset": items[0].value[1:-1], "outdir": items[1].value[1:-1], "format": str(items[2])}

def parse_script(text):
    parser = Lark(GRAMMAR, parser="lalr", transformer=ScriptTransformer())
    return parser.parse(text)