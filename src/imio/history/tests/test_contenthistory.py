from zope.component import getMultiAdapter
from Products.Five import zcml

from plone import api
from imio import history as imio_history
from imio.history.config import HISTORY_COMMENT_NOT_VIEWABLE
from imio.history.testing import IntegrationTestCase


class TestContentHistory(IntegrationTestCase):

    def setUp(self):
        super(TestContentHistory, self).setUp()
        # get the viewlet
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
        self.assertTrue(len(history) == 1 and history[0]['action'] is None)
        # publish the doc
        self.wft.doActionFor(self.doc, 'publish')
        history = view.getHistory()
        # actions are sorted reverse so first element of history is still last action
        self.assertTrue(len(history) == 2 and history[0]['action'] == 'publish')

        # when changing an element workflow, getHistory will return events
        # of the currently applied workflow
        self.wft.setChainForPortalTypes(('Document', ), ('intranet_workflow',))
        # when we changed the workflow for an element, it still does not changed
        # the workflow_history so change workflow state for it to happen
        self.wft.doActionFor(self.doc, 'hide')
        # now using getHistory will return right history
        history = view.getHistory()
        self.assertTrue(len(history) == 1 and history[0]['action'] == 'hide')

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
        # are viewable in the object's workflow history
        # create a document and publish it, the comment of the 'publish' transition is viewable
        # create a document
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
