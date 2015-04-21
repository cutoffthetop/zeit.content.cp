from zeit.cms.testcontenttype.testcontenttype import TestContentType
import lxml.etree
import mock
import zeit.cms.interfaces
import zeit.content.cp.interfaces
import zeit.content.cp.testing
import zeit.edit.interfaces
import zope.component
import zope.interface.interfaces


class AutomaticAreaSolrTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaSolrTest, self).setUp()
        self.repository['cp'] = zeit.content.cp.centerpage.CenterPage()

    def test_fills_with_placeholders_when_set_to_automatic(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = 'query'
        self.assertEqual(5, len(lead))

    def test_fills_with_placeholders_when_teaser_count_changed(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = 'query'
        self.assertEqual(5, len(lead))
        auto.count = 7
        self.assertEqual(7, len(lead))

    def tests_values_contain_only_blocks_with_content(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = 'query'
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            self.assertEqual(0, len(auto.values()))

    def test_only_marked_articles_are_put_into_leader_block(self):
        self.repository['normal'] = TestContentType()
        leader = TestContentType()
        leader.lead_candidate = True
        self.repository['leader'] = leader

        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 2
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [dict(uniqueId='http://xml.zeit.de/normal'),
                                   dict(uniqueId='http://xml.zeit.de/leader')]
            result = auto.values()
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_no_marked_articles_available_leader_block_gets_normal_article(
            self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            result = auto.values()
        leader = result[0]
        self.assertEqual(
            'http://xml.zeit.de/testcontent', list(leader)[0].uniqueId)

    def test_no_marked_articles_leader_block_layout_is_changed_virtually(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent')]
            result = auto.values()
        leader = result[0]
        self.assertEqual('buttons', leader.layout.id)
        self.assertEqual('leader', lead.values()[0].layout.id)
        self.assertEllipsis('...module="buttons"...', lxml.etree.tostring(
            zeit.content.cp.interfaces.IRenderedXML(leader),
            pretty_print=True))

    def test_renders_xml_with_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent',
                     lead_candidate=True)]
            xml = zeit.content.cp.interfaces.IRenderedXML(lead)
        self.assertEllipsis(
            """\
<region...>
  <container...type="teaser"...>
    <block...href="http://xml.zeit.de/testcontent"...""",
            lxml.etree.tostring(xml, pretty_print=True))

    def test_rendered_xml_contains_automatic_items_in_cp_feed(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent',
                     lead_candidate=True)]
            xml = zeit.content.cp.interfaces.IRenderedXML(
                self.repository['cp'])
        self.assertEllipsis(
            """...
<feed>
  <reference...href="http://xml.zeit.de/testcontent"...""",
            lxml.etree.tostring(xml, pretty_print=True))

    def test_cms_content_iter_returns_filled_in_blocks(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.automatic = 'query'

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [
                dict(uniqueId='http://xml.zeit.de/testcontent',
                     lead_candidate=True)]
            content = zeit.content.cp.interfaces.ICMSContentIterable(auto)
            self.assertEqual(
                ['http://xml.zeit.de/testcontent'],
                [x.uniqueId for x in content])

    def test_stores_query_in_xml(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        self.assertEqual((), auto.query)
        auto.query = (
            ('Channel', 'International', 'Nahost'),
            ('Channel', 'Wissen', None))
        self.assertEllipsis(
            """<...
            <query>
              <condition...type="Channel"...>International Nahost</condition>
              <condition...type="Channel"...>Wissen</condition>
            </query>...""", lxml.etree.tostring(auto.xml, pretty_print=True))

    def test_prefers_raw_query_if_present(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.raw_query = 'raw'
        auto.automatic = 'query'
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            auto.values()
            self.assertEqual('raw', search.call_args[0][0])

    def test_builds_query_from_conditions(self):
        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 1
        auto.query = (
            ('Channel', 'International', 'Nahost'),
            ('Channel', 'Wissen', None),
            ('Keyword', 'Berlin', None))
        auto.automatic = 'channel'
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            auto.values()
            query = search.call_args[0][0]
            self.assertIn('published:(published*)', query)
            self.assertIn(
                '(channels:(International*Nahost)'
                ' OR channels:(Wissen*)'
                ' OR keywords:(Berlin*))',
                query)

    def test_turning_automatic_off_materializes_filled_in_blocks(self):
        self.repository['normal'] = TestContentType()
        leader = TestContentType()
        leader.lead_candidate = True
        self.repository['leader'] = leader

        lead = self.repository['cp']['lead']
        auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
        auto.count = 5
        auto.automatic = 'query'
        zope.component.getAdapter(
            lead, zeit.edit.interfaces.IElementFactory, name='rss')()

        with mock.patch('zeit.find.search.search') as search:
            search.return_value = [dict(uniqueId='http://xml.zeit.de/normal'),
                                   dict(uniqueId='http://xml.zeit.de/leader')]
            auto.automatic = 'false'

        result = lead.values()
        self.assertEqual(
            ['teaser', 'teaser', 'rss'], [x.type for x in result])
        self.assertEqual(
            'http://xml.zeit.de/leader', list(result[0])[0].uniqueId)
        self.assertEqual(
            'http://xml.zeit.de/normal', list(result[1])[0].uniqueId)

    def test_checkin_smoke_test(self):
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            with zeit.cms.checkout.helper.checked_out(
                    self.repository['cp']) as cp:
                lead = cp['lead']
                auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
                auto.count = 1
                auto.automatic = 'query'

    def test_channel_has_automatic_attribute(self):
        with mock.patch('zeit.find.search.search') as search:
            search.return_value = []
            with zeit.cms.checkout.helper.checked_out(
                    self.repository['cp']) as cp:
                lead = cp['lead']
                auto = zeit.content.cp.interfaces.IAutomaticArea(lead)
                auto.count = 1
                auto.automatic = 'query'
        self.assertEqual(
            'True', self.repository['cp.lead'].xml.get('automatic'))


class AutomaticAreaCenterPageTest(zeit.content.cp.testing.FunctionalTestCase):

    def setUp(self):
        super(AutomaticAreaCenterPageTest, self).setUp()
        self.cp = zeit.content.cp.centerpage.CenterPage()
        self.area = zeit.content.cp.interfaces.IAutomaticArea(
            self.cp['feature'].create_item('area'))
        self.repository['cp'] = self.cp

        cp_with_teaser = zeit.content.cp.centerpage.CenterPage()
        self.repository['t1'] = TestContentType()
        self.repository['t2'] = TestContentType()
        self.repository['t3'] = TestContentType()
        cp_with_teaser['lead'].create_item('teaser').insert(
            0, self.repository['t1'])
        cp_with_teaser['lead'].create_item('teaser').insert(
            1, self.repository['t2'])
        cp_with_teaser['lead'].create_item('teaser').insert(
            2, self.repository['t3'])
        self.repository['cp_with_teaser'] = cp_with_teaser

        self.area.referenced_cp = self.repository['cp_with_teaser']
        self.area.count = 3
        self.area.automatic = 'centerpage'

    def test_returns_teasers_from_referenced_center_page(self):
        self.assertEqual([
            'http://xml.zeit.de/t1',
            'http://xml.zeit.de/t2',
            'http://xml.zeit.de/t3'],
            [list(x)[0].uniqueId for x in self.area.values()])

    def test_yields_centerpage_in_addition_to_teaser_when_iterating(self):
        content = zeit.content.cp.interfaces.ICMSContentIterable(self.cp)
        self.assertEqual([
            u'http://xml.zeit.de/cp_with_teaser',
            u'http://xml.zeit.de/t1',
            u'http://xml.zeit.de/t2',
            u'http://xml.zeit.de/t3'],
            [x.uniqueId for x in content])

    def test_automatic_from_centerpage_requires_referenced_centerpage(self):
        self.area.referenced_cp = None
        with self.assertRaises(zeit.cms.interfaces.ValidationError):
            interface = zeit.content.cp.interfaces.IAutomaticArea
            interface.validateInvariants(self.area)

    def test_automatic_using_solr_requires_no_referenced_centerpage(self):
        self.area.referenced_cp = None
        self.area.automatic = 'query'
        with self.assertNothingRaised():
            interface = zeit.content.cp.interfaces.IAutomaticArea
            interface.validateInvariants(self.area)
