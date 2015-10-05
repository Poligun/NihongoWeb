from nihongo.models import *
from itertools import combinations
from nihongo.dictionary import Hiraganas, Katakanas
from collections import defaultdict

def collect():
    charMap = {}
    for word in Word.objects.all():
        for comb in combinations(range(len(word.kana) - 1), len(word.word)):
            indices = [0] +list(map(lambda num: num + 1, sorted(comb)))
            separation = [word.kana[indices[i]:indices[i + 1]] for i in range(len(indices) - 1)] + [word.kana[indices[-1]:]]
            for i in range(len(word.word)):
                char = word.word[i]
                if char in Hiraganas or char in Katakanas:
                    continue
                if char not in charMap:
                    charMap[char] = defaultdict(lambda: 0)
                charMap[char][separation[i]] += 1
    for char in charMap:
        charMap[char] = sorted(charMap[char].items(), key = lambda e: -e[1])
    return charMap

charMap = collect()