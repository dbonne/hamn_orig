#!/usr/bin/env python

import datetime

import feedparser

from hamnadmin.register.models import Post

class FeedFetcher(object):
	def __init__(self, feed, tracefunc=None):
		self.feed = feed
		self.tracefunc = tracefunc
		self.newest_entry_date = None

	def _trace(self, msg):
		if self.tracefunc:
			self.tracefunc(msg)

	def parse(self, fetchsince=None):
		if fetchsince:
			parser = feedparser.parse(self.feed.feedurl, modified=fetchsince.timetuple())
		else:
			parser = feedparser.parse(self.feed.feedurl)

		if not hasattr(parser, 'status'):
			# bozo_excpetion can seemingly be set when there is no error as well,
			# so make sure we only check if we didn't get a status.
			if hasattr(parser, 'bozo_exception'):
				raise Exception('Feed load error %s' % parser.bozo_exception)
			raise Exception('Feed load error with no exception!')

		if parser.status == 304:
			# Not modified
			return

		if parser.status != 200:
			# XXX: follow redirect?
			raise Exception('Feed returned status %s' % parser.status)

		self._trace("Fetched %s, status %s" % (self.feed.feedurl, parser.status))

		if self.feed.blogurl == '':
			try:
				self.feed.blogurl = parser.feed.link
			except:
				pass

		for entry in parser.entries:
			if not self.matches_filter(entry):
				self._trace("Entry %s does not match filter, skipped" % entry.link)
				continue

			# Grab the entry. At least atom feeds from wordpress store what we
			# want in entry.content[0].value and *also* has a summary that's
			# much shorter.
			# We therefor check all available texts, and just pick the one that
			# is longest.
			txtalts = []
			try:
				txtalts.append(entry.content[0].value)
			except:
				pass
			if entry.has_key('summary'):
				txtalts.append(entry.summary)

			# Select the longest text
			txt = max(txtalts, key=len)
			if txt == '':
				self._trace("Entry %s has no contents" % entry.link)
				continue

			dat = None
			if hasattr(entry, 'published_parsed'):
				dat = datetime.datetime(*(entry.published_parsed[0:6]))
			elif hasattr(entry, 'updated_parsed'):
				dat = datetime.datetime(*(entry.updated_parsed[0:6]))
			else:
				self._trace("Failed to get date for entry %s (keys %s)" % (entry.link, entry.keys()))
				continue

				if self.newest_entry_date:
					if dat > self.newest_entry_date:
						self.newest_entry_date = dat
				else:
					self.newest_entry_date = dat

			yield Post(feed=self.feed,
					   guid=entry.id,
					   link=entry.link,
					   txt=txt,
					   dat=dat,
					   title=entry.title,
					   )


		# Check if we got back a Last-Modified time
		if hasattr(parser, 'modified_parsed') and parser['modified_parsed']:
			# Last-Modified header retreived. If we did receive it, we will
			# trust the content (assuming we can parse it)
			d = datetime.datetime(*parser['modified_parsed'][:6])
			if (d-datetime.datetime.now()).days > 5:
				# Except if it's ridiculously long in the future, we'll set it
				# to right now instead, to deal with buggy blog software. We
				# currently define rediculously long as 5 days
				d = datetime.datetime.now()

			self.feed.lastget = d
			self.feed.save()
		else:
			# We didn't get a Last-Modified time, so set it to the entry date
			# for the latest entry in this feed.
			if self.newest_entry_date:
				self.feed.lastget = self.newest_entry_date
				self.feed.save()

	def matches_filter(self, entry):
		# For now, we only match against self.feed.authorfilter. In the future,
		# there may be more filters.
		if self.feed.authorfilter:
			# Match against an author filter

			if entry.has_key('author_detail'):
				return entry.author_detail.name == self.feed.authorfilter
			elif entry.has_key('author'):
				return entry.author == self.feed.authorfilter
			else:
				return False

		# No filters, always return true
		return True
