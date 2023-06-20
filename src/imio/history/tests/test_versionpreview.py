# -*- coding: utf-8 -*-

from imio.history.testing import IntegrationTestCase
from plone import api


class TestVersionPreview(IntegrationTestCase):

    """Test IHVersionPreviewView, it is there to be registered for relevant content types."""

    def test_view(self):
        doc = api.content.create(
            type='Document',
            id='doc',
            title="Document title 1",
            container=self.portal)
        # make 2 new versions of doc and change title each time
        pr = self.portal.portal_repository
        pr.save(obj=doc)
        doc.setTitle("Document title 2")
        doc.reindexObject(idxs=['Title', ])
        pr.save(obj=doc)
        doc.setTitle("Document title 3")
        doc.reindexObject(idxs=['Title', ])
        # the view __call__ receives a version_id
        # it will store in self.versioned_object the version_id object
        # so it is available in the template
        view = doc.restrictedTraverse('@@history-version-preview')
        # current
        self.assertEqual(view.context.Title(), "Document title 3")
        # version_id 1
        view(version_id=1)
        self.assertEqual(view.versioned_object.Title(), "Document title 1")
        # version_id 2
        view(version_id=2)
        self.assertEqual(view.versioned_object.Title(), "Document title 2")
