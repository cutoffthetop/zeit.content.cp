# Copyright (c) 2009-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.content.cp.browser.blocks.teaser
import zeit.content.cp.interfaces
import zeit.edit.browser.block
import zeit.edit.browser.view
import zeit.edit.interfaces
import zope.formlib.form


class ViewletManager(zeit.edit.browser.block.BlockViewletManager):

    @property
    def css_class(self):
        classes = super(ViewletManager, self).css_class
        return ' '.join(['editable-area', classes])


class EditProperties(zeit.content.cp.browser.blocks.teaser.EditLayout):

    interface = zeit.content.cp.interfaces.IArea
    layout_prefix = 'teaserbar'  # XXX should be area


class EditCommon(zeit.edit.browser.view.EditBox):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IArea).select(
            'width', 'supertitle', 'title', 'teaserText', '__name__')

    def validate(self, action, data):
        errors = super(EditCommon, self).validate(action, data)
        try:
            data['__context__'] = self.context
            zeit.edit.interfaces.unique_name_invariant(
                zeit.cms.browser.form.AttrDict(**data))
        except Exception as e:
            errors.append(e)
        return errors


class ChangeLayout(zeit.content.cp.browser.blocks.teaser.ChangeLayout):

    interface = zeit.content.cp.interfaces.IArea
