"""
Test conversion of markdown to HTML

"""
import jinja2
import markdown

with open('test.md', 'r') as fp:
    md = fp.read()


print(md)

html = markdown.markdown(md)

print(html)
# search
# login
