# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.browser.menu
import zeit.cms.checkout.interfaces


class MenuItem(zeit.cms.browser.menu.LightboxActionMenuItem):

    sort = -1
    lightbox = '@@publish.html'

    def is_visible(self):
        manager = zeit.cms.checkout.interfaces.ICheckinManager(self.context)
        return manager.canCheckin

    # XXX duplicated from zeit.cms.checkout.browser.MenuItem
    def render(self):
        if self.is_visible():
            return super(MenuItem, self).render()
        return ''
