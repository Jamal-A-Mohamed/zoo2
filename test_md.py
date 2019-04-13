"""
Test conversion of markdown to HTML

"""
import markdown

with open('test.md', 'r') as fp:
    md = fp.read()


print(md)

html = markdown.markdown(md)

print(html)


# search
# login
#
# import mediawiki_parser as parser
# from mediawiki_parser import html
# with open('wikitext.txt', 'r', encoding='UTF-8') as fp:
#     source = fp.read()
# templates = {}
# allowed_tags = []
# allowed_self_closing_tags = []
# allowed_attributes = []
# interwiki = {}
# namespaces = {}
#
# from mediawiki_parser.preprocessor import make_parser
# preprocessor = make_parser(templates)
#
# from mediawiki_parser.html import make_parser
# parser = make_parser(allowed_tags, allowed_self_closing_tags, allowed_attributes, interwiki, namespaces)
#
# preprocessed_text = preprocessor.parse(source)
# output = parser.parse(preprocessed_text.leaves())
# print(output)
#
# html.make_parser()
#


