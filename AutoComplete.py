from collections import defaultdict

class AutoComplete:
    def __init__(self, wordSet):
        self.prefixMap = defaultdict(set)
        for word in wordSet:
            word = word.lower()
            for i in range(1, min(len(word), 15)):
                self.prefixMap[word[:i]].add(word)

    def suggest(self, prefix, limit=10):
        prefix = prefix.lower()
        return list(self.prefixMap.get(prefix, []))[:limit]
