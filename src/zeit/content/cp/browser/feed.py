# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.interfaces
import zeit.cms.interfaces
import zeit.cms.repository.browser.adapter
import zope.publisher.interfaces


class ListRepresentation(
    zeit.cms.repository.browser.adapter.CMSContentListRepresentation):

    zope.component.adapts(zeit.content.cp.interfaces.IFeed,
                          zope.publisher.interfaces.IPublicationRequest)

    @property
    def title(self):
        return self.context.title