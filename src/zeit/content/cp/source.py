import zeit.cms.content.sources
import zope.dottedname.resolve


class CPTypeSource(zeit.cms.content.sources.SimpleContextualXMLSource):
    # we are contextual so we can set a default value, but have it not validated
    # at import time, since we don't have our product config then, yet.

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-types-url'

    def getValues(self, context):
        tree = self._get_tree()
        return [unicode(item.get('name'))
                for item in tree.iterchildren()]

    def getTitle(self, context, value):
        __traceback_info__ = (value, )
        tree = self._get_tree()
        return unicode(tree.xpath('/centerpage-types/type[@name = "%s"]' %
                                  value)[0])


class CPExtraSource(zeit.cms.content.sources.XMLSource):

    product_configuration = 'zeit.content.cp'
    config_url = 'cp-extra-url'
    attribute = 'id'

    def getValues(self, context):
        tree = self._get_tree()
        result = []
        for element in tree.iterchildren():
            for_ = zope.dottedname.resolve.resolve(element.get('for'))
            if for_.providedBy(context.__parent__):
                result.append(unicode(element.get('id')))
        return result