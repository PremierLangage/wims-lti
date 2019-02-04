from django.test import TestCase

from wims.templatetags.markdown import markdown



class TTMarkdownTestCase(TestCase):
    
    def test_markdown(self):
        self.assertEqual("<h1>A Title</h1>", markdown("# A Title"))
        self.assertEqual("<ul>\n<li>elem1</li>\n<li>elem2</li>\n</ul>",
                         markdown("* elem1\n* elem2"))
