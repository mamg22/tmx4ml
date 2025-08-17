import re

import bbcode
import yarl

parser = bbcode.Parser(
    newline="\n",
    install_defaults=False,
    replace_cosmetic=False,
    drop_unrecognized=True,
    url_template="$l[{href}]{text}$l",
)

parser.add_simple_formatter("b", "$s%(value)s$s", strip=True)
parser.add_simple_formatter("i", "$i%(value)s$i", strip=True)
parser.add_simple_formatter("u", "$i%(value)s$i", strip=True)
parser.add_simple_formatter("s", "$n%(value)s$m", strip=True)
parser.add_simple_formatter("img", "$l[%(value)s]<image>$l", strip=True)
parser.add_simple_formatter("tmx", "$oTrackmania$d22Exchange$g$o", standalone=True)
parser.add_simple_formatter("mx", "$oMania$7dfExchange$g$o", standalone=True)


TAG_TO_ITEM = {
    "track": "track",
    "user": "user",
    "pack": "trackpack"
}


def format_item(
    tag_name: str, value: str, options: dict[str, str], parent, context: dict[str, str]
) -> str:
    value = value.strip()
    url = yarl.URL(context["origin"]) / context["site"] / TAG_TO_ITEM[tag_name.lower()] / value

    return f"$h[{url}]<{tag_name}:{value}>$h"


parser.add_formatter("track", format_item)
parser.add_formatter("user", format_item)
parser.add_formatter("pack", format_item)


def format_bbcode(source: str, origin: str, site: str) -> str:
    escaped = source.replace("$", "$$")
    reduced = re.sub(r"(\r?\n)+", "\n", escaped)

    return parser.format(reduced, origin=origin, site=site)


__all__ = ["format_bbcode"]
