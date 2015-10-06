from zope.component import getMultiAdapter
from Products.Five import zcml

from plone import api
from plone.app.testing import TEST_USER_NAME

from imio import history as imio_history
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.testing import IntegrationTestCase


class TestContentHistory(IntegrationTestCase):

    def setUp(self):
        super(TestContentHistory, self).setUp()
        doc = api.content.create(type='Document',
                                 id='doc',
                                 container=self.portal)
        self.doc = doc

    def test_getHistory(self):
        """Test the getHistory method.
           It should return the history of the current object workflow
           in reverse order, last event first."""
        # create a document
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        # we can get the workflow history even when no transition was triggered
        history = view.getHistory()
        # this is the 'element created' event in the history
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['action'], 'Edited')
        self.assertEqual(history[0]['type'], 'versioning')
        self.assertEqual(history[0]['actor'], TEST_USER_NAME)
        self.assertIsNone(history[1]['action'])
        self.assertEqual(history[1]['type'], 'workflow')
        # publish the doc
        self.wft.doActionFor(self.doc, 'publish')
        history = view.getHistory()
        # actions are sorted reverse so first element of history is still last action
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['action'], 'publish')

        # when changing an element workflow, getHistory will return events
        # of the currently applied workflow
        self.wft.setChainForPortalTypes(('Document', ), ('intranet_workflow',))
        # when we changed the workflow for an element, it still does not changed
        # the workflow_history so change workflow state for it to happen
        self.wft.doActionFor(self.doc, 'hide')
        # now using getHistory will return right history
        history = view.getHistory()
        self.assertEqual(history[0]['action'], 'hide')

        # test that it works if element has no more workflow defined in portal_workflow
        # define no workflow anymore for 'Document'
        self.wft.setChainForPortalTypes(('Document', ), [])
        for event in view.getHistory():
            self.assertNotEqual(event['type'], 'workflow')

        # test that it works also with an element having no workflow
        # and so no workflow_history attribute
        # we will test with type 'File' that does not have a workflow by default
        fileType = self.portal.portal_types['File']
        self.assertTrue(self.wft.getWorkflowsFor(fileType) == [])
        afile = api.content.create(type='File',
                                   id='afile',
                                   container=self.portal)
        view = getMultiAdapter((afile, self.portal.REQUEST), name='contenthistory')
        # no workflow_history attribute
        self.assertTrue(not hasattr(afile, 'workflow_history'))
        # this does not fail
        self.assertTrue(view.getHistory() == [])

    def test_getTransitionTitle(self):
        """Test the getTransitionTitle method.
           This will return the title of a transition if it has one, the id otherwise."""
        # create a document
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        # it use the 'simple_publication_workflow'
        # test with an existing transition
        self.assertTrue(view.getTransitionTitle('publish') == 'Reviewer publishes content')
        # if the transition does not exist, it will return passed transition id
        self.assertTrue(view.getTransitionTitle('unexisting_transition_id') == 'unexisting_transition_id')
        # if a transition does not have a title, the passed transition id is returned
        self.wft.simple_publication_workflow.transitions['publish'].title = ''
        self.assertTrue(view.getTransitionTitle('publish') == 'publish')

    def test_showColors(self):
        """Test the showColors method.
           This is defined to be easily overrided, for now it is always True."""
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        self.assertTrue(view.showColors())

    def test_MayViewComment(self, ):
        """Test the mayViewComment method.
           We will register an adapter that test when it is overrided."""
        # by default, mayViewComment returns "True" so every comments
        # are viewable in the object's history
        # create a document and publish it, the comment of the 'publish' transition is viewable
        self.wft.doActionFor(self.doc, 'publish', comment='My comment')
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        history = view.getHistory()
        lastEvent = history[0]
        self.assertTrue(lastEvent['action'] == 'publish')
        self.assertTrue(lastEvent['comments'] == 'My comment')

        # now register an adapter that will do 'publish' transition comment not visible
        zcml.load_config('testing-adapter.zcml', imio_history)
        history = view.getHistory()
        lastEvent = history[0]
        self.assertTrue(lastEvent['action'] == 'publish')
        # now comment is no more viewable
        self.assertTrue(lastEvent['comments'] == HISTORY_COMMENT_NOT_VIEWABLE)

        # getHistory can be called with checkMayView set to False,
        # in this case, mayViewComment check is not done
        history = view.getHistory(checkMayView=False)
        lastEvent = history[0]
        self.assertTrue(lastEvent['action'] == 'publish')
        # comment is viewable as mayViewComment was not done
        self.assertTrue(lastEvent['comments'] == 'My comment')
        # cleanUp zmcl.load_config because it impact other tests
        zcml.cleanUp()

    def test_showRevisionInfos(self):
        """Test the showRevisionInfos method."""
        pr = api.portal.get_tool('portal_repository')
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')

        # As the type of doc is a versionable content, showRevisionInfo should
        # return True.
        self.assertTrue(view.showRevisionInfos())
        # Remove the type "Document" from the versionable content.
        pr.setVersionableContentType([u'ATDocument', u'ATNewsItem', u'Event', u'Link', u'News Item'])
        # Now showRevisionInfos shoud return False.
        self.assertFalse(view.showRevisionInfos())

    def test_renderComments(self):
        """Test the renderComments method."""
        # render comments will first try to translate the comments
        # then turn it from 'text/plain' to 'text/html'
        view = getMultiAdapter((self.doc, self.portal.REQUEST), name='contenthistory')
        self.assertEquals(view.renderComments('data_change'),
                          u'<p>Data change</p>')
        self.assertEquals(view.renderComments('Custom comments not translatable.\nAnd one additional line.'),
                          u'<p>Custom comments not translatable.<br />And one additional line.</p>')
