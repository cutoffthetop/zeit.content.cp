# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.content.cp.i18n import MessageFactory as _
import zeit.edit.browser.view
import zope.interface
import zope.security.proxy
import zope.traversing.browser


class Editor(object):

    title = _('Edit centerpage')

    def validate(self, area):
        validation_class, validation_messages = (
            zeit.edit.browser.view.validate(area))
        css_class = ['editable-area']
        if validation_class:
            css_class.append(validation_class)
        css_class = ' '.join(css_class)
        return dict(class_=css_class, messages=validation_messages)


class Migrate(zeit.cms.workingcopy.browser.workingcopy.DeleteFromWorkingcopy):

    current_iface = zeit.content.cp.interfaces.ICP2009
    other_iface = zeit.content.cp.interfaces.ICP2015

    def __call__(self):
        if self.request.method != 'POST':
            return super(Migrate, self).__call__()
        self.delete()
        return self.request.response.redirect(
            self.next_url(self.context.__parent__))

    @property
    def content_type(self):
        for iface in [self.other_iface, self.current_iface]:
            if iface.providedBy(self.context):
                return iface.__name__
