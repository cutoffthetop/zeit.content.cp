# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import mock
import unittest
import zeit.cms.testing
import zeit.content.cp.testing


class TestTeaserDisplay(unittest.TestCase):

    def setUp(self):
        from zeit.content.cp.browser.blocks.teaser import Display
        display = Display()
        display.context = mock.Mock()
        display.request = mock.Mock()
        display.layout = mock.Mock()
        display.url = mock.Mock()
        self.display = display
        self.content = mock.Mock()

    def test_get_image_should_use_preview_when_no_iimages(self):
        with mock.patch('zope.component.queryMultiAdapter') as qma:
            image = self.display.get_image(self.content)
            qma.assert_called_with((self.content, self.display.request),
                                   name='preview')
            self.display.url.assert_called_with(qma())
            self.assertEqual(image, self.display.url())

    def test_get_image_should_not_break_with_no_iimages_and_no_preview(self):
        self.assertTrue(self.display.get_image(self.content) is None)


class TestTeaserSupertitle(zeit.cms.testing.BrowserTestCase):

    layer = zeit.content.cp.testing.layer

    def test_no_teaser_supertitle_present_shows_supertitle_instead(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    self.repository['testcontent']) as co:
                    co.supertitle = 'bar'

        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')
        b.open(contents_url)
        self.assertEllipsis(
            '...<div class="supertitle">bar</div>...', b.contents)

    def test_if_teaser_supertitle_present_it_takes_precedence_over_supertitle(self):
        with zeit.cms.testing.site(self.getRootFolder()):
            with zeit.cms.testing.interaction():
                with zeit.cms.checkout.helper.checked_out(
                    self.repository['testcontent']) as co:
                    co.teaserSupertitle = 'foo'
                    co.supertitle = 'bar'

        b = self.browser
        zeit.content.cp.browser.testing.create_cp(b)
        b.open('contents')
        contents_url = b.url
        b.open(
            'lead/@@landing-zone-drop?uniqueId=http://xml.zeit.de/testcontent')
        b.open(contents_url)
        self.assertEllipsis(
            '...<div class="supertitle">foo</div>...', b.contents)
