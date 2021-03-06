from zeit.content.cp.i18n import MessageFactory as _
import zeit.cms.interfaces
import zeit.content.cp.browser.blocks.block
import zeit.content.cp.interfaces
import zeit.content.video.interfaces
import zeit.edit.browser.view
import zope.formlib.form
import zope.lifecycleevent


class EditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IAVBlock).omit(
            *list(zeit.content.cp.interfaces.IBlock))


class VideoEditProperties(zeit.content.cp.browser.blocks.block.EditCommon):

    form_fields = zope.formlib.form.Fields(
        zeit.content.cp.interfaces.IVideoBlock).select(
            'media_type', 'id', 'player', 'expires', 'format')


class DropVideo(zeit.edit.browser.view.Action):
    """Drop a video to a video block."""

    uniqueId = zeit.edit.browser.view.Form('uniqueId')

    def update(self):
        content = zeit.cms.interfaces.ICMSContent(self.uniqueId)
        if not zeit.content.video.interfaces.IVideoContent.providedBy(
                content):
            raise ValueError(_(
                "Only videos and playlists can be dropped on a video block."))
        # There is the assumption that the __name__ is unique for all videos
        # and playlists. This is true for the current brightcove implementation
        # but might change at some point (unlikely though).
        self.context.id = content.__name__
        if zeit.content.video.interfaces.IVideo.providedBy(content):
            self.context.player = u'vid'
            self.context.expires = content.expires
        else:
            self.context.player = u'pls'
            self.context.expires = None
        zope.lifecycleevent.modified(self.context)
        self.reload()
