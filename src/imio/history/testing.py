from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

import imio.history


IMIO_HISTORY = PloneWithPackageLayer(
    zcml_package=imio.history,
    zcml_filename='testing.zcml',
    gs_profile_id='imio.history:testing',
    name="IMIO_HISTORY")

IMIO_HISTORY_INTEGRATION = IntegrationTesting(
    bases=(IMIO_HISTORY, ),
    name="IMIO_HISTORY_INTEGRATION")

IMIO_HISTORY_FUNCTIONAL = FunctionalTesting(
    bases=(IMIO_HISTORY, ),
    name="IMIO_HISTORY_FUNCTIONAL")
