import os
import sys
sys.path.append("AOGCpy3")

import Chunker
import XMLRule
import SentenceSplitter
import Tokenizer
import SpellingChecker
import AOStemmer
import RulesLoader
import RuleMatch
import Tagger
sys.path.append(...)
from collections import Counter

class TextChecker:
	"""main class"""
	def __init__(self):
		self.spellCheck = SpellingChecker.SpellingChecker()
		self.tokenizer = Tokenizer.Tokenizer()
		self.tagger = Tagger.Tagger()
		self.chunker = Chunker.Chunker()
		self.rules = RulesLoader.Rules()
		self.stemmer = AOStemmer.AOStemmer()
		return
		
	def checkFile(self, filename):
		"""Check a text file and return the results as an XML formatted list 
		of possible errors."""
		f = open(filename)
		text = f.read()
		f.close()
		# (rule_matches, result, tagged_words) = self.check(text)
		result = self.check(text)
		# return (rule_matches, result, tagged_words)
		return result

	def check(self, text):
		"""Check a text string and return the results as an XML formatted list 
		of possible errors."""
		splitter = SentenceSplitter.SentenceSplitter()
		sentences = splitter.split(text)
		# print('SENTEN: ', sentences)
		rule_matches = []
		char_counter = 0
		all_tagged_words = []
		all_untagged = []
		flag = 0
		error_index = []
		wholeSpellCheck = {}
		finalResult = {}
		for i, sentence in enumerate(sentences):
			if not sentence: 
				continue
			tokenList, tokenList_for_whitespace = self.tokenizer.tokenizer(sentence)
			correctionDict = self.spellCheck.spellCheck(tokenList)
			if correctionDict:
				wholeSpellCheck.update(correctionDict)
			tagged_words = self.tagger.tag(tokenList)
			# print ('TAGGED: ', tagged_words)
			tagged_plus_affix = self.stemmer.stemTokenList([i for i in tagged_words])
			# print ("TAG+AF: ", tagged_plus_affix)
			chunks = self.chunker.chunk(tagged_plus_affix)
			# print ("CHUNKS: ", chunks)
			all_tagged_words.extend(tagged_plus_affix)
			all_untagged.extend(tokenList_for_whitespace)
			for rule in self.rules.rules:
				if rule.rule_id == 'WHITESPACE':
					whitespacerule = rule
					continue
				matches = rule.match(tagged_plus_affix, chunks, char_counter)
				if matches:
					error_index.append(i)
					# finalResult["grammar"] = [match.message() for match in matches]
				rule_matches.extend(matches)
			for triple in sentence:
				char_counter = char_counter + len(triple[0])
		
		finalResult["spell"] = wholeSpellCheck
		
		# print(finalResult)
		general = False
		white_space_match = whitespacerule.match(all_untagged)
		if white_space_match:
			rule_matches.extend(white_space_match)
			general = True

		rule_match_dic = {}
		index1 = 0
		for rule_match in rule_matches:
			# if index1 <= len(error_index)-1:
			# 	rule_match_dic.append(sentences[error_index[index1]].strip())
			# elif general:
			# 	rule_match_dic.append("General Rule")
			if rule_match.errorWord():
				rule_match_dic[rule_match.errorWord()] = [rule_match.message]
			else:
				f = rule_match.f_pos()
				t = rule_match.t_pos()+1
				rule_match_dic[text[f:t]] = [rule_match.message]
			index1 = index1 + 1
		finalResult["grammar"] = rule_match_dic
		# return (rule_matches, finalResult, all_tagged_words)
		return finalResult

# def main():
# 	checker = TextChecker()
# 	# (rule_matches, result, tagged_words) = checker.checkFile('testcase.txt')
# 	result = checker.checkFile('testcase.txt')
# 	if not result:
# 		print ("No errors found.")
# 	else:
# 		# pass
# 		print (result)
# 		# print (rule_matches)
# 		# print (tagged_words)
# 	return

# if __name__ == "__main__":
# 	textcheckerobj = TextChecker()
# 	result = textcheckerobj.check("akm ati sol")
# 	print(result)
# 	main()
	
