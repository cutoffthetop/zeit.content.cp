from zeit.cms.checkout.helper import checked_out
from zeit.cms.workflow.interfaces import IPublish
from zeit.content.cp.centerpage import CenterPage
from zeit.content.cp.interfaces import ICP2009, ICP2015
import gocept.cache.method
import pkg_resources
import zeit.cms.testing
import zeit.content.cp.testing
import zeit.workflow.testing
import zope.interface


class MigrateTest(zeit.cms.testing.FunctionalTestCase):

    layer = zeit.content.cp.testing.layer

    def test_new_cp_provides_current_interface(self):
        self.repository['cp'] = CenterPage()
        with checked_out(self.repository['cp']):
            pass
        self.assertTrue(ICP2009.providedBy(self.repository['cp']))

    def test_publish_does_not_cycle_mismatched_cp(self):
        # Clear rules cache so we get the empty ruleset, so we can publish.
        gocept.cache.method.clear()
        zope.app.appsetup.product.getProductConfiguration(
            'zeit.edit')['rules-url'] = 'file://%s' % (
                pkg_resources.resource_filename(
                    'zeit.content.cp.tests.fixtures', 'empty_rules.py'))

        self.repository['cp'] = CenterPage()
        with checked_out(self.repository['cp']) as cp:
            zope.interface.noLongerProvides(cp, ICP2009)
            zope.interface.alsoProvides(cp, ICP2015)
        before_publish = zeit.cms.workflow.interfaces.IModified(
            self.repository['cp']).date_last_checkout
        IPublish(self.repository['cp']).publish()
        zeit.workflow.testing.run_publish()
        after_publish = zeit.cms.workflow.interfaces.IModified(
            self.repository['cp']).date_last_checkout
        self.assertEqual(before_publish, after_publish)


class MigrateBrowserTest(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def setUp(self):
        super(MigrateBrowserTest, self).setUp()
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                self.repository['cp'] = CenterPage()
                with checked_out(self.repository['cp']) as cp:
                    zope.interface.noLongerProvides(cp, ICP2009)
                    zope.interface.alsoProvides(cp, ICP2015)
        self.browser.open(
            'http://localhost/++skin++vivi/repository/cp/@@checkout')

    def test_old_cp_show_warning_instead_of_editor(self):
        b = self.browser
        self.assertEllipsis('...Attention...', b.contents)

    def test_abort_deletes_workingcopy(self):
        b = self.browser
        b.getControl('Cancel').click()
        self.assertIn('/repository/', b.url)
        self.assertFalse(ICP2009.providedBy(self.repository['cp']))
