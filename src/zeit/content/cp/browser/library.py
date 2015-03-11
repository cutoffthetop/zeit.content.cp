"""Module library and landing zones.

The module library allows users to create new blocks.

See http://cmsdev.zeit.de/node/362

"""

import lxml.objectify
import zeit.edit.browser.library


class CPBlockFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        xml = lxml.objectify.XML('<dummy/>')
        return zeit.content.cp.area.Area(None, xml)

    @property
    def library_name(self):
        return 'cp'


class CPAreaFactories(zeit.edit.browser.library.BlockFactories):

    @property
    def factory_context(self):
        xml = lxml.objectify.XML('<dummy/>')
        return zeit.content.cp.area.Region(None, xml)

    @property
    def library_name(self):
        return 'region'

    def get_adapters(self):
        return [{
            'name': area_config.id,
            'type': 'area',
            'title': area_config.title,
            'library_name': self.library_name,
            'params': {'width': area_config.width}
        } for area_config in zeit.content.cp.layout.AREA_CONFIGS(self.context)]
