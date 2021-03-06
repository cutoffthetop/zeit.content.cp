Centerpage
==========

[#functional]_

>>> import zeit.content.cp.centerpage
>>> cp = zeit.content.cp.centerpage.CenterPage()
>>> cp
<zeit.content.cp.centerpage.CenterPage...>
>>> cp.type = u'homepage'
>>> cp.type
u'homepage'


The ancient XML representation looked as follows:

>>> import lxml.etree
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage... type="homepage"...>
  <head>...
  <body>
    <cluster area="feature">
      <region area="lead"/>
      <region area="informatives"/>
    </cluster>
    <cluster area="teaser-mosaic"/>
  </body>
  <feed/>
</centerpage>
>>> import zeit.connector.interfaces
>>> print zeit.connector.interfaces.IWebDAVProperties(cp)[
...     ('type', 'http://namespaces.zeit.de/CMS/zeit.content.cp')]
homepage



Other areas are not accessible:

>>> cp['ugc-bar']
Traceback (most recent call last):
    ...
KeyError: 'ugc-bar'

The centerpage is reachable via ``__parent__`` or by adapting to it:

>>> cp['feature'].__parent__
<zeit.content.cp.centerpage.Body...>
>>> import zeit.content.cp.interfaces
>>> zeit.content.cp.interfaces.ICenterPage(cp['feature'])
<zeit.content.cp.centerpage.CenterPage...>

[#modified-handler]_


Header image
++++++++++++

>>> import zeit.cms.repository.interfaces
>>> import zope.component
>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> cp.header_image = repository['2006']['DSC00109_2.JPG']
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...>
<head>
...
<header_image src="http://xml.zeit.de/2006/DSC00109_2.JPG"...>
...
</centerpage>


Topic Links
+++++++++++

>>> cp.topiclink_title = 'Sachsen Linkse'
>>> cp.topiclink_label_1 = 'Sachsen spezial'
>>> cp.topiclink_url_1 = 'http://www.zeit.de/themen/sachsen/index'
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...>
  <head>
...
    <topiclinks>
      <topiclink_title...>Sachsen Linkse</topiclink_title>
      <topiclink>
        <topiclink_label_1...>Sachsen spezial</topiclink_label_1>
        <topiclink_url_1...>http://www.zeit.de/themen/sachsen/index</topiclink_url_1>
      </topiclink>
    </topiclinks>
  ...
</centerpage>


OG-Metadata
+++++++++++

>>> cp.og_title = 'Isch bin da Title'
>>> cp.og_description = 'Hier geht die Description'
>>> cp.og_image = 'yo-man.jpg'
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...>
  <head>
...
    <og_meta>
       <og_title...>Isch bin da Title</og_title>
       <og_description...>Hier geht die Description</og_description>
       <og_image...>yo-man.jpg</og_image>
    </og_meta>
  ...
</centerpage>


Blocks
++++++

A block is part of an area.

Teaser block
------------

>>> informatives = cp['informatives']
>>> import zeit.content.cp.interfaces
>>> import zope.component
>>> factory = zope.component.getAdapter(
...     informatives, zeit.edit.interfaces.IElementFactory,
...     name='teaser')
>>> factory.title
u'List of teasers'
>>> block = factory()
>>> block
<zeit.content.cp.blocks.teaser.TeaserBlock...>
>>> block.type
'teaser'

After calling the factory a corresponding XML node has been created:

>>> print lxml.etree.tostring(informatives.xml, pretty_print=True),
<region ... area="informatives"...>
  <container cp:type="teaser" module="leader" ... cp:__name__="..."/>
</region>


Modules are accessible via __getitem__ [#invalid-raises-error]_:

>>> informatives[block.__name__]
<zeit.content.cp.blocks.teaser.TeaserBlock...>

The area can also be iterated:

>>> list(informatives.itervalues())
[<zeit.content.cp.blocks.teaser.TeaserBlock...>]
>>> informatives.values()
[<zeit.content.cp.blocks.teaser.TeaserBlock...>]

It is possible to get the center page from the block by adapting to ICenterPage:

>>> zeit.content.cp.interfaces.ICenterPage(block)
<zeit.content.cp.centerpage.CenterPage...>

The ``__parent__`` of a block is the area:

>>> block.__parent__
<zeit.content.cp.area.Area...>


Areas support ordering of their contents via the ``updateOrder`` method:

>>> transaction.commit()
>>> [block_key] = informatives.keys()
>>> block.__name__ == block_key
True
>>> informatives.updateOrder([block_key])
>>> informatives.keys() == [block_key]
True
>>> cp._p_changed
True

The keys have not changed:

>>> block.__name__ == block_key
True


[#invalid-arguments-to-updateorder]_

Blocks can be removed using __delitem__:

>>> transaction.commit()
>>> len(informatives)
1
>>> del informatives[block.__name__]
>>> len(informatives)
0
>>> informatives.values()
[]
>>> cp._p_changed
True


Checkin handler
+++++++++++++++

When the centerpage is checked in, the metadata of all its articles need to be
updated [#needsinteraction]_.

Before we can begin, we need to put our centerpage into the repository so that
we can check it out:

>>> repository = zope.component.getUtility(
...     zeit.cms.repository.interfaces.IRepository)
>>> repository['cp'] = cp
>>> cp = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['cp']).checkout()

Now we need some test objects we can edit later on:

>>> factory = zope.component.getAdapter(
...     cp['lead'], zeit.edit.interfaces.IElementFactory, name='teaser')
>>> teasers = factory()
>>> import zeit.cms.repository.interfaces
>>> teaser = zeit.content.cp.teaser.Teaser()
>>> teaser.original_content = repository['testcontent']
>>> repository['testcontent-1'] = teaser
>>> teaser = repository['testcontent-1']
>>> teasers.insert(0, repository['testcontent'])
>>> teasers.insert(1, teaser)

Edit the referenced article while the centerpage is checked out:

>>> testcontent = zeit.cms.checkout.interfaces.ICheckoutManager(
...     repository['testcontent']).checkout()
>>> testcontent.teaserTitle = 'Foo'
>>> dummy = zeit.cms.checkout.interfaces.ICheckinManager(testcontent).checkin()

When we now check in the centerpage, the changes in our article are propagated.
We also check that the teaser object contains a link to its original article:

>>> cp = zeit.cms.checkout.interfaces.ICheckinManager(cp).checkin()
>>> import gocept.async.tests
>>> gocept.async.tests.process()
>>> cp = repository['cp']
>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage ...
<block href="http://xml.zeit.de/testcontent"...
  <title py:pytype="str">Foo</title>...
<block href="http://xml.zeit.de/testcontent"...
       uniqueId="http://xml.zeit.de/testcontent-1"...>...


Content referenced in a centerpage has additional dates on the node:

>>> print lxml.etree.tostring(cp.xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released=""
         date-last-published=""
         last-semantic-change=""...


Make a semantic change to testcontent:

>>> import zeit.cms.checkout.helper
>>> with zeit.cms.checkout.helper.checked_out(repository['testcontent'],
...                                           semantic_change=True):
...     pass

The metadata is updated (asynchronously) when the centerpage is checked in:

>>> with zeit.cms.checkout.helper.checked_out(repository['cp']):
...     pass
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released=""
         date-last-published=""
         last-semantic-change="2009-09-11T08:18:48+00:00"...

Publish test content:

>>> zeit.cms.workflow.interfaces.IPublishInfo(
...     repository['testcontent']).urgent = True
>>> job_id = zeit.cms.workflow.interfaces.IPublish(
...     repository['testcontent']).publish()
>>> import lovely.remotetask.interfaces
>>> tasks = zope.component.getUtility(
...     lovely.remotetask.interfaces.ITaskService, 'general')
>>> tasks.process()

The data is, again, updated when the CP is checked in:

>>> with zeit.cms.checkout.helper.checked_out(repository['cp']):
...     pass
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <block href="http://xml.zeit.de/testcontent"...
         date-last-modified="2009-09-11T08:18:48+00:00"
         date-first-released="2009-09-11T08:18:48+00:00"
         date-last-published="2009-09-11T08:18:48+00:00"
         last-semantic-change="2009-09-11T08:18:48+00:00"...


Referenced images
+++++++++++++++++

>>> img = repository['2006']['DSC00109_2.JPG']
>>> with zeit.cms.checkout.helper.checked_out(repository['cp']) as co:
...     co.header_image = img
>>> with zeit.cms.checkout.helper.checked_out(img) as co:
...     zeit.content.image.interfaces.IImageMetadata(co).title = 'updated'
>>> gocept.async.tests.process()
>>> print lxml.etree.tostring(repository['cp'].xml, pretty_print=True)
<centerpage...
  <header_image... title="updated"...>
...

Topic page
==========


>>> topic_provider = zope.component.getUtility(
...     zeit.cms.sitecontrol.interfaces.ISitesProvider, name='topicpage')
>>> import pprint
>>> pprint.pprint(list(topic_provider))
[<zeit.cms.repository.unknown.PersistentUnknownResource...>,
 <zeit.cms.repository.unknown.PersistentUnknownResource...>,
 <zeit.cms.repository.unknown.PersistentUnknownResource...>]


.. [#needsinteraction]

    >>> principal = zeit.cms.testing.create_interaction()


.. [#functional]

    >>> import zeit.cms.testing
    >>> zeit.cms.testing.set_site()


.. [#modified-handler] The centerpages need to be nodified when sub location
    change. When we modify an area the centerpage will be considered changed:

    >>> import transaction
    >>> import zope.event
    >>> import zope.lifecycleevent
    >>> getRootFolder()['cp'] = cp
    >>> transaction.commit()  # Commit to actually be able to "change"
    >>> zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(
    ...     cp['lead']))
    >>> cp._p_changed
    True

    There is also such a handler for IObjectMovedEvent:

    >>> transaction.commit()
    >>> import zope.container.contained
    >>> zope.event.notify(zope.container.contained.ObjectMovedEvent(
    ...     cp['lead'], None, None, None, None))
    >>> cp._p_changed
    True


.. [#invalid-raises-error]

    >>> informatives['foo']
    Traceback (most recent call last):
        ...
    KeyError: 'foo'

.. [#invalid-arguments-to-updateorder] Invalid arguments to update order raise
    errors as defined in the interface:

    >>> informatives.updateOrder(124)
    Traceback (most recent call last):
        ...
    TypeError: order must be tuple or list, got <type 'int'>.

    >>> informatives.updateOrder(['abc', 'def'])
    Traceback (most recent call last):
        ...
    ValueError: order must have the same keys.
