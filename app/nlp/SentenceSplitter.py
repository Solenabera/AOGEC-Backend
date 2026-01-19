import string
import re
from pathlib import Path

class SentenceSplitter:

	BASE_DIR = Path(__file__).resolve().parent.parent
	ABBR_FILE = BASE_DIR / "data" / "abbr.txt"
	# ABBR_FILE = "Files/abbr.txt"
	
	EOS = "<>"		# temporary end determiner
	P = """[\.!?]"""				## PUNCTUATION
	AP = """(?:'|"|�|\)|\]|\})?"""	## AFTER PUNCTUATION
	PAP = "%s%s" % (P, AP) #[\.!?](?:'|"|�|\)|\]|\})?
	
	def __init__(self):
		"""Init the object by loading the abbreviation list."""
		self.abbr = self.importAbbr()
		return

	def importAbbr(self):
		"""Import the abbreviation list in abbr.txt and return all words in a list."""
		abbr = []
		f = open(self.ABBR_FILE, "r")
		while 1:
			l = f.readline()
			if not l:
				break
			l = l.strip()
			if l:
				abbr.append(l)
		f.close()
		return abbr
		
	def split(self, text):
		"""Take a paragraph and split it into sentences. 
		   Return the list of sentences."""
		if text == None:
			return []
		marked_text = self.first_sentence_breaking(text)
		print("Marked text: ", marked_text)
		fixed_marked_text = self.remove_false_end_of_sentence(marked_text)
		fixed_marked_text = self.split_unsplit_stuff(fixed_marked_text)
		print("Fixed Marked text: ", fixed_marked_text)
		sentences = re.split(self.EOS, fixed_marked_text)
		return sentences

	def first_sentence_breaking(self, text):
		"""Add a special break character at all places with typical sentence
		delimiters."""
		# Double new-line means a new sentence:
		text = re.compile("\n\s*\n", re.DOTALL).sub(self.EOS, text)
		# Punctuation followed by whitespace means a new sentence:
		text = re.compile("(%s\s)" % self.PAP, re.DOTALL).sub("\\1%s" % self.EOS, text)
		# Punctuation followed by uppercase followed by non-uppercase
		# (except dot) means a new sentence:
		text = re.compile("(%s)([%s][^%s.])" % (self.PAP, string.ascii_uppercase, string.ascii_uppercase), \
			re.DOTALL).sub("\\1%s\\2" % self.EOS, text)
		# Break also when single letter comes before punctuation:
		text = re.compile("(\s\w%s)" % self.P, re.DOTALL).sub("\\1%s" % self.EOS, text)
		#print "Punc + single letter: ",text
		return text
		
	def remove_false_end_of_sentence(self, text):
		"""Repair some positions that don't require a split, i.e. remove the
		special break character."""
		
		# Don't split at e.g. "U. S. A.":
		text = re.compile("([^-\w]\w%s\s)%s" % (self.PAP, self.EOS), re.DOTALL).sub("\\1", text)
		# Don't split at e.g. "U.S.A.":
		text = re.compile("([^-\w]\w%s)%s" % (self.P, self.EOS), re.DOTALL).sub("\\1", text)

		# Don't split after a white-space followed by a single letter followed
		# by a dot followed by another whitespace.
		# e.g. " p. "
		text = re.compile("(\s\w\.\s+)%s" % self.EOS, re.DOTALL).sub("\\1", text)

		# Don't split at "bla bla... yada yada" (TODO: use \.\.\.\s+ instead?)
		text = re.compile("(\.\.\. )%s([%s])" % (self.EOS, string.ascii_lowercase), re.DOTALL).sub("\\1\\2", text)
		# Don't split [.?!] when the're quoted:
		text = re.compile("(['\"]%s['\"]\s+)%s" % (self.P, self.EOS)).sub("\\1", text)
		# Don't split at abbreviations:
		for abbr in self.abbr:
			# TODO: really ignore case?
			s = "(\\b%s%s\s)%s" % (abbr, self.PAP, self.EOS)
			text = re.compile(s, re.DOTALL|re.IGNORECASE).sub("\\1", text)
		# Don't break after quote unless there's a capital letter:
		# e.g.: "That's right!" he said.
		text = re.compile('(["\']\s*)%s(\s*[%s])' % (self.EOS, string.ascii_lowercase), re.DOTALL).sub("\\1\\2", text)

		# fixme? not sure where this should occur, leaving it commented out:
		# don't break: text . . some more text.
		#text=~s/(\s\.\s)$EOS(\s*)/$1$2/sg;

		text = re.compile("(\s%s\s)%s" % (self.PAP, self.EOS), re.DOTALL).sub("\\1", text)

		# extension by dnaber --commented out, doesn't help:
		#text = re.compile("(:\s+)%s(\s*[%s])" % (self.EOS, string.lowercase), re.DOTALL).sub("\\1\\2", text)
		return text

	def split_unsplit_stuff(self, text):
		"""Treat some more special cases that make up a sentence boundary. Insert
		the special break character at these positions."""
		# Split at e.g. "no. 5 ":
		text = re.compile("(\D\d+)(%s)(\s+)" % self.P, re.DOTALL).sub("\\1\\2%s\\3" % self.EOS, text)
		# TODO: Not sure about this one, leaving out foir now:
		#text = re.compile("(%s\s)(\s*\()" % self.PAP, re.DOTALL).sub("\\1%s\\2" % self.EOS, text)
		# Split e.g.: He won't. #Really.
		text = re.compile("('\w%s)(\s)" % self.P, re.DOTALL).sub("\\1%s\\2" % self.EOS, text)
		# Split e.g.: He won't say no. Not really.
		text = re.compile("(\sno\.)(\s+)(?!\d)", re.DOTALL|re.IGNORECASE).sub("\\1%s\\2" % self.EOS, text)
		# Split at "a.m." or "p.m." followed by a capital letter.
		text = re.compile("([ap]\.m\.\s+)([%s])" % string.ascii_uppercase, re.DOTALL).sub("\\1%s\\2" % self.EOS, text)
		return text

if __name__ == "__main__":
	sample = ["I love U.S.A. very much.",'"Do split me." Will you?',
			"This is e.g. Mr. Smith, who talks slowly... But this is another sentence."]
	sample2 = ["US unveils world's most powerful supercomputer, beats China. The US \
has unveiled the world's most powerful supercomputer called 'Summit', \
beating the previous record-holder China's Sunway TaihuLight. With a \
peak performance of 200,000 trillion calculations per second, it is over \
twice as fast as Sunway TaihuLight, which is capable of 93,000 trillion \
calculations per second. Summit has 4,608 servers, which reportedly take up \
the size of two tennis courts."]
	
	# print (sample)
	sp = SentenceSplitter()
	for i in sample2:
		sent = sp.split(i)
		print (sent)
