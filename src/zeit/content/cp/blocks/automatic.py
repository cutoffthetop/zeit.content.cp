import gocept.lxml.interfaces
import grokcore.component as grok
import zeit.content.cp.blocks.block
import zeit.content.cp.interfaces
import zeit.edit.block
import zope.component
import zope.interface


class AutomaticTeaserBlock(zeit.content.cp.blocks.block.Block):

    zope.interface.implements(
        zeit.content.cp.interfaces.IAutomaticTeaserBlock,
        zope.container.interfaces.IContained)

    zope.component.adapts(
        zeit.content.cp.interfaces.IArea,
        gocept.lxml.interfaces.IObjectified)

    def __init__(self, context, xml):
        super(AutomaticTeaserBlock, self).__init__(context, xml)
        self.entries = []
        self.temporary_layout = None
        # XXX copy&paste from TeaserBlock
        if self.xml.get('module') == 'auto-teaser':
            self.layout = self.layout
        assert self.xml.get('module') != 'auto-teaser'

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)

    def insert(self, index, content):
        self.entries.insert(index, content)

    def __getattr__(self, name):
        if name in zeit.content.cp.interfaces.ITeaserBlock:
            return zeit.content.cp.interfaces.ITeaserBlock[name].default
        raise AttributeError(name)

    def update_topiclinks(self):
        pass

    # XXX copy&paste&tweak from TeaserBlock
    @property
    def layout(self):
        if self.temporary_layout:
            return self.temporary_layout
        default = None
        for layout in zeit.content.cp.interfaces.ITeaserBlock['layout'].source(
                self):
            if layout.id == self.xml.get('module'):
                return layout
            if layout.default:
                default = layout
        return default

    @layout.setter
    def layout(self, layout):
        self._p_changed = True
        self.xml.set('module', layout.id)

    def change_layout(self, layout):
        self.temporary_layout = layout


zeit.edit.block.register_element_factory(
    zeit.content.cp.interfaces.IArea, 'auto-teaser')


@grok.adapter(zeit.content.cp.interfaces.IAutomaticTeaserBlock)
@grok.implementer(zeit.content.cp.interfaces.ICMSContentIterable)
def cms_content_iter(context):
    for teaser in context:
        yield teaser
