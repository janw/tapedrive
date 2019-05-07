from urllib.parse import urlparse

from bleach.utils import force_unicode
from bleach.sanitizer import BleachSanitizerFilter, Cleaner
from html5lib.filters.base import Filter

from django.utils.text import format_lazy


CLEAN_HTML_GLOBAL = ["summary", "subtitle"]
CLEAN_HTML_EPISODE = ["description", "subtitle"]

ALLOWED_HTML_TAGS = [
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "p",
    "strong",
    "ul",
]

ALLOWED_HTML_ATTRIBUTES = {
    "a": ["href", "title"],
    "acronym": ["title"],
    "abbr": ["title"],
}

EXTENDED_HTML_TAGS = [
    "h1",
    "h2",
    "h3" "h4",
    "h5",
    "h6",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
]

EXTENDED_HTML_ATTRIBUTES = {"img": ["rel", "src", "alt"], "td": ["colspan", "rowspan"]}


def clean_link(link, include_path=False):
    parsed = urlparse(link)
    netloc = parsed.netloc
    if parsed.netloc.startswith("www."):
        netloc = netloc[4:]

    if include_path:
        path = parsed.path.rstrip("/")
        splits = str.split(path, "/")
        if len(splits) > 2:
            path = "/…/" + splits[-1]

        return netloc + path
    return netloc


class CleanerWithOptions(Cleaner):
    def clean(self, text, allowed_domains=False):
        if not allowed_domains:
            allowed_domains = []

        if not isinstance(text, str):
            message = "argument cannot be of '{name}' type, must be of text type".format(
                name=text.__class__.__name__
            )
            raise TypeError(message)

        if not text:
            return ""

        text = force_unicode(text)
        dom = self.parser.parseFragment(text)
        filtered = BleachSanitizerFilter(
            source=self.walker(dom),
            # Bleach-sanitizer-specific things
            attributes=self.attributes,
            strip_disallowed_elements=self.strip,
            strip_html_comments=self.strip_comments,
            # html5lib-sanitizer things
            allowed_elements=self.tags,
            allowed_css_properties=self.styles,
            allowed_protocols=self.protocols,
            allowed_svg_properties=[],
        )

        # Apply any filters after the BleachSanitizerFilter
        for filter_class in self.filters:
            fc = filter_class(source=filtered)
            filtered = fc.__iter__(allowed_domains=allowed_domains)

        return self.serializer.render(filtered)


class ImgSrcFilter(Filter):
    def __iter__(self, **kwargs):
        allowed_domains = kwargs.pop("allowed_domains", [])
        for token in Filter.__iter__(self):
            if token["type"] in ["StartTag", "EmptyTag"] and token["data"]:
                data_alt = None
                data_src = None
                for attr, value in token["data"].items():
                    if attr[1] in ("alt", "src"):
                        data_alt = value

                if data_src:
                    domain = clean_link(data_src)
                    if domain not in allowed_domains:
                        token["data"][(None, "data-src")] = data_src
                        token["data"][(None, "class")] = "has-src"
                        token["data"][(None, "alt")] = format_lazy(
                            "Image from {domain}", domain=domain
                        )
                        token["data"][(None, "src")] = ""
                        if data_alt:
                            token["data"][(None, "data-alt")] = data_alt
            yield token


subtitle_cleaner = Cleaner(tags=[], strip=True)

summary_cleaner = Cleaner(
    tags=ALLOWED_HTML_TAGS, attributes=ALLOWED_HTML_ATTRIBUTES, strip=True
)

shownotes_cleaner = Cleaner(
    tags=ALLOWED_HTML_TAGS + EXTENDED_HTML_TAGS,
    attributes={**ALLOWED_HTML_ATTRIBUTES, **EXTENDED_HTML_ATTRIBUTES},
    strip=True,
)

shownotes_image_cleaner = CleanerWithOptions(
    tags=ALLOWED_HTML_TAGS + EXTENDED_HTML_TAGS,
    attributes={**ALLOWED_HTML_ATTRIBUTES, **EXTENDED_HTML_ATTRIBUTES},
    strip=True,
    filters=[ImgSrcFilter],
)
