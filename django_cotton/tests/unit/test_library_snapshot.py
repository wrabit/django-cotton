from django.template import Template
from django.test import SimpleTestCase

from django_cotton.templatetags._component import CottonComponentNode


class LibrarySnapshotTests(SimpleTestCase):
    def test_components_share_snapshot_until_load_changes_it(self):
        template = Template(
            "{% cotton a / %}{% cotton b / %}{% load static %}{% cotton c / %}"
        )
        a, b, c = template.nodelist.get_nodes_by_type(CottonComponentNode)

        self.assertIs(a.active_library, b.active_library)
        self.assertIsNot(b.active_library, c.active_library)
        self.assertNotIn("static", b.active_library.tags)
        self.assertIn("static", c.active_library.tags)
