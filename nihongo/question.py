from nihongo.models import *
from nihongo.algorithm import getLcs, weightedSample
from nihongo.dictionary import Hiraganas, Katakanas, katakanaToHiragana
import random

pickWord = lambda: random.choice(Word.objects.all())

def startTest():
    #word = Word.objects.filter(word = '打ち合わせ')[0]
    word = pickWord()
    print('{} - {}'.format(word.word, word.kana))
    print(makeChoices(word.word, word.kana))

def pickSimilarKana(kana):
    row, col = getRowAndCol(kana)
    while True:
        newCol = weightedSample(range(5), lambda c: 5 - abs(min(col - c, col + 5 - c)), 1)[0]
        newKana = Hiraganas[row * 5 + newCol]
        if row in [1, 2, 3, 4, 5, 6, 8, 9 ,10]:
            # TO-DO: 增加選擇清濁的功能
            pass
        if newKana in 'ゃゅょっんを':
            continue
        return newKana

def makeChoices(word, kana, numberOfChoices = 5):
    word = katakanaToHiragana(word)
    lcs = getLcs(word, kana)
    choices = []
    while len(choices) < numberOfChoices:
        choice = ''
        lcsCopy = lcs
        # TO-DO: 首先確定選項中變化的假名個數以及比例
        for i in range(len(kana)):
            if kana[i] in 'ゃゅょっんを':
                choice += kana[i]
                continue
            if len(lcsCopy) > 0 and kana[i] == lcsCopy[0]:
                lcsCopy = lcsCopy[1:]
                choice += kana[i]
                continue
            # TO-DO: 針對促音及拗音部分檢查合法性
            choice += pickSimilarKana(kana[i])
        if choice != kana and choice not in choices:
            choices.append(choice)
    choices.append(kana)
    random.shuffle(choices)
    return choices

def generateKanaQuestion(word):
    candidates = []
    for w in Word.objects.all():
        length = len(getLcs(word.kana, w.kana))
        if min(len(word.kana) - 1, 1) <= length < len(word.kana):
            candidates.append([w, length])
    candidateFilter = list(filter(lambda e: e[1] / len(e[0].kana) > 0.4, candidates))
    if len(candidateFilter) > 0:
        candidates = candidateFilter
    options = [word] + [e[0] for e in weightedSample(candidates, lambda e: e[1], 5)]
    random.shuffle(options)
    for i in range(len(options)):
        if options[i] == word:
            return { 'options': options, 'answer': i }


def generateBlankQuestion(word):
    exampleCandidates = []
    for meaning in word.meaning_set.all():
        for example in meaning.example_set():
            if example.occurence_set.count() == 1:
                exampleCandidates.append(example)
    example = random.choice(exampleCandidates)

def getRowAndCol(kana):
    index = Hiraganas.index(kana)
    return (index // 5, index % 5)

def getDist(kana1, kana2):
    row1, col1 = getRowAndCol(kana1)
    row2, col2 = getRowAndCol(kana2)
    return 0.5 * abs(row1 - row2) + 1.5 * abs(col1 - col2)

Hiraganas = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'さ', 'し', 'す', 'せ', 'そ',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'た', 'ち', 'つ', 'て', 'と', 
    'だ', 'ぢ', 'づ', 'で', 'ど',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    'ま', 'み', 'む', 'め', 'も',
    'ら', 'り', 'る', 'れ', 'ろ',
    'や', 'ゃ', 'ゆ', 'ゅ', 'よ',
    'わ', 'ん', 'っ', 'ょ', 'を'
]

Katakanas = [
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'バ', 'ビ', 'ブ', 'ベ', 'ボ',
    'パ', 'ピ', 'プ', 'ペ', 'ポ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ヤ', 'ャ', 'ユ', 'ュ', 'ヨ',
    'ワ', 'ン', 'ッ', 'ョ', 'ヲ',
    'ヰ', 'ヱ'
]
