# coding: utf8
# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt
"""Landing zone views.

See: http://cmsdev.zeit.de/content/aufmacher-fläche-einen-block-anlegen-durch-ziehen-eines-content-objekts

"""

import zeit.cms.related.interfaces
import zope.browser.interfaces
import zeit.content.cp.browser.view
import zope.component


class LandingZone(zeit.content.cp.browser.view.Action):

    def update(self):
        self.create_block()
        self.initialize_block()
        self.update_order()
        self.signal('after-reload', 'added', self.block.__name__)

    def create_block(self):
        factory = zope.component.getAdapter(
            self.create_in, zeit.content.cp.interfaces.IElementFactory,
            name=self.block_type)
        self.block = factory()

    def initialize_block(self):
        pass

    def update_order(self):
        order = list(self.create_in)
        order.remove(self.block.__name__)
        order = self.get_order(order, self.block.__name__)
        self.create_in.updateOrder(order)

    @property
    def create_in(self):
        if self.order == 'after-context':
            return self.context.__parent__
        return self.context

    def get_order(self, order, new_name):
        if isinstance(self.order, int):
            order.insert(self.order, new_name)
        elif self.order == 'after-context':
            after = order.index(self.context.__name__)
            order.insert(after + 1, new_name)
        else:
            raise NotImplementedError
        return order


class TeaserBlockLandingZone(LandingZone):

    block_type = 'teaser'
    uniqueId = zeit.content.cp.browser.view.Form('uniqueId')

    def initialize_block(self):
        pass
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        self.block.insert(0, content)
        related = zeit.cms.related.interfaces.IRelatedContent(content, None)
        if related is not None:
            for i, related in enumerate(related.related):
                self.block.insert(i+1, related)


class LeaderLandingZoneDrop(TeaserBlockLandingZone):
    """Handler to drop articles on the lead landing zone."""

    order = 0


class TeaserLandingZoneInsertAfter(TeaserBlockLandingZone):

    order = 'after-context'
