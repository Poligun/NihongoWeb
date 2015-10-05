import re
import bs4, os.path
import urllib.request, urllib.parse

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

PunctuationMapping = {
    ',': '，',
    '.': '。',
    ';': '；',
    '“': '「',
    '”': '」',
    '/': '／',
    '(': '（',
    ')': '）',
    '［': '（',
    '］': '）',
    '~': '～',
    '。。。': '……',
    '・・・': '……',
}

Adan = [Hiraganas[i * 5 + 0] for i in range(14)]
Idan = [Hiraganas[i * 5 + 1] for i in range(13)]
Udan = [Hiraganas[i * 5 + 2] for i in range(14)]
Edan = [Hiraganas[i * 5 + 3] for i in range(13)]
Odan = [Hiraganas[i * 5 + 4] for i in range(14)]

MappingFilePath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mapping.txt')
Mappings = (lambda: dict([(components[0], components[1:]) for components in \
    map(lambda line: line.strip().split(' '), open(MappingFilePath, encoding = 'utf8').read().split('\n')) \
    if len(components) > 0]))()

def parseWordType(rawType):
    types = []
    for type in re.findall('【[^】]+】', rawType):
        for t in filter(lambda e: e != '', re.split(r'[•・·･▪，.【】\ ]+', type)):
            if t in Mappings:
                types += Mappings[t]
            else:
                raise Exception('Mapping not found for raw type: "{}"'.format(t))
    return list(set(types))

def katakanaToHiragana(string):
    for char in string:
        if char in Katakanas:
            string = string.replace(char, Hiraganas[Katakanas.index(char)])
    return string

def parseKana(kana):
    """
    kana = kana.strip().replace('【', '').replace('】', '')
    return katakanaToHiragana(kana)
    """
    parsed = ''
    for char in kana:
        if char in Hiraganas:
            parsed += char
        elif char in Katakanas:
            parsed += Hiraganas[Katakanas.index(char)]
    return parsed

def getAdjectiveForms(adj):
    lastKana = adj[-1]
    adj = adj[:-1]
    if lastKana != 'い' and lastKana != 'イ':
        raise Exception('Adjective must end in "い".')
    return {
        '連用形': '{}く'.format(adj),
        '過去形': '{}かった'.format(adj)
    }

#TO_DO なさい形　たい形
def getVerbForms(verb, type = '一段动词'):
    if type == 'サ变动词':
        verb = verb.replace('する', '')
        forms = getVerbForms('する', '五段动词')
        for key, value in forms.items():
            forms[key] = '{}{}'.format(verb, value)
        return forms

    lastKana = verb[-1]
    verb = verb[:-1]

    if lastKana not in Udan:
        raise Exception('Verb must end in "う段仮名".')

    if type ==  '一段动词':
        renyouKei = verb
        teKei     = '{}て'.format(verb)
        kakoKei   = '{}た'.format(verb)
        hiteiKei  = '{}'.format(verb)
        shiekiKei = hiteiKei
        shiekiUkemi = '{}させられ'.format(verb)
        kateiKei  = '{}ば'.format(verb)
        ukemiKei  = '{}られ'.format(verb)
        kanouKei  = '{}れ'.format(verb)
        ishiKei   = '{}よう'.format(verb)
        meireiKei = '{}ろ'.format(verb)

    elif type == '五段动词':
        row = Hiraganas.index(lastKana) // 5
        renyouKei = verb + Idan[row]
        hiteiKei  = verb + ('わ' if lastKana == 'う' else Adan[row])
        shiekiKei = hiteiKei
        shiekiUkemi = '{}れ'.format(hiteiKei)
        kateiKei  = verb + Edan[row] + 'ば'
        ukemiKei  = hiteiKei + 'れ'
        kanouKei  = verb + Edan[row]
        ishiKei   = verb + Odan[row] + 'う'
        meireiKei = verb + Edan[row]

        if lastKana in ['う', 'つ', 'る']:
            teKei = '{}って'.format(verb)
            kakoKei = '{}った'.format(verb)

        elif lastKana in ['す']:
            teKei = '{}して'.format(verb)
            kakoKei = '{}した'.format(verb)

        elif lastKana in ['く']:
            teKei = '{}いて'.format(verb)
            kakoKei = '{}いた'.format(verb)

        elif lastKana in ['ぐ']:
            teKei = '{}いで'.format(verb)
            kakoKei = '{}いだ'.format(verb)

        elif lastKana in ['ぬ', 'ぶ', 'む']:
            teKei = '{}んで'.format(verb)
            kakoKei = '{}んだ'.format(verb)

        """ Handle Special Cases """
        original = verb + lastKana

        if original == '行く':
            teKei = '行って'
            kakoKei = '行った'
        elif original == 'いく':
            teKei = 'いって'
            kakoKei = 'いった'
        elif original == 'ゆく':
            teKei = 'ゆって'
            kakoKei = 'ゆった'

        if original == '来る':
            renyouKei = hiteiKei = '来'
            teKei = '来て'
            kakoKei = '来た'
        elif original == 'くる':
            renyouKei = 'き'
            hiteiKei = 'こ'
            teKei = 'きて'
            kakoKei = 'きた'

        if original == 'する':
            renyouKei = 'し'
            teKei     = 'して'
            kakoKei   = 'した'
            hiteiKei  = 'し'
            kateiKei  = 'すれば'
            ukemiKei  = 'され'
            kanouKei  = 'でき'
            shiekiKei = 'さ'
            shiekiUkemi = 'させられ'
            ishiKei   = 'しよう'
            meireiKei = 'しろ'

        if verb == 'いらっしゃ':
            renyouKei = 'いらっしゃい'

    forms = {
        'ます形': '{}ます'.format(renyouKei),
        '辞書形': '{}{}'.format(verb, lastKana),
        '連用形': renyouKei,
        '連用形（お）': 'お{}'.format(renyouKei),
        'て形': teKei,
        '仮定形': kateiKei,

        '過去形（ました）': '{}ました'.format(renyouKei),
        '過去形（た）': kakoKei,

        '否定形（ません）': '{}ません'.format(renyouKei),
        '否定形（ない）': '{}ない'.format(hiteiKei),
        '否定形（なく）': '{}なく'.format(hiteiKei),
        '否定形（ず）': '{}ず'.format(hiteiKei),
        '否定形（ぬ）': '{}ぬ'.format(hiteiKei),

        '否定形（仮定）': '{}なければ'.format(hiteiKei),

        '過去否定形（ませんでした）': '{}ませんでした'.format(renyouKei),
        '過去否定形（なかった）': '{}なかった'.format(hiteiKei),

        '受身形（ます）': '{}ます'.format(ukemiKei),
        '受身形（辞書）': '{}る'.format(ukemiKei),
        '受身形（て形）': '{}て'.format(ukemiKei),

        '可能形（ます）': '{}ます'.format(kanouKei),
        '可能形（辞書）': '{}る'.format(kanouKei),
        '可能形（ません）': '{}ません'.format(kanouKei),
        '可能形（ない）': '{}ない'.format(kanouKei),

        '使役形（ます）': '{}せます'.format(shiekiKei),
        '使役形（辞書）': '{}せる'.format(shiekiKei),
        '使役形（て形）': '{}せて'.format(shiekiKei),

        '使役受身形（ます）': '{}ます'.format(shiekiUkemi),
        '使役受身形（辞書）': '{}る'.format(shiekiUkemi),
        '使役受身形（ません）': '{}ません'.format(shiekiUkemi),
        '使役受身形（ない）': '{}ない'.format(shiekiUkemi),
        '使役受身形（されました）': '{}ました'.format(shiekiUkemi),
        '使役受身形（された）': '{}た'.format(shiekiUkemi),

        '意志形': ishiKei,
        '命令形': meireiKei,
    }

    if type == '五段动词':
        if original == 'する':
            forms['否定形（ず）'] = 'せず'
            forms['否定形（ぬ）'] = 'せぬ'
            del forms['連用形']
            del forms['連用形（お）']

    return forms

def getForms(word, kana, wordTypes):
    forms = []
    if '一类形容词' in wordTypes:
        forms += [getAdjectiveForms(word), getAdjectiveForms(kana)]
    elif '一段动词' in wordTypes:
        forms += [getVerbForms(word, type = '一段动词'), getVerbForms(kana, type = '一段动词')]
    elif '五段动词' in wordTypes:
        forms += [getVerbForms(word, type = '五段动词'), getVerbForms(kana, type = '五段动词')]
    elif 'サ变动词' in wordTypes:
        forms += [getVerbForms(word, type = 'サ变动词'), getVerbForms(kana, type = 'サ变动词')]
    forms = [v for form in forms for k, v in form.items()] + [word, kana]
    return sorted((list(set(forms))), key = lambda f: -len(f))

def parseEntry(entry):
    entry = entry.replace('\u3000', '').strip()
    for key, value in PunctuationMapping.items():
        entry = entry.replace(key, value)
    entry = re.sub(r'[A-Za-z]{2,}', '', entry)
    entry = re.sub('^（[0-9]+）', '', entry)
    entry = entry.replace('（）', '')
    return entry

def parseExample(entry, word, wordForms):
    components = re.split(r'／+', entry)
    if len(components) < 2:
        raise Exception('Bad example "{}".'.format(entry))
    example, translation = components[0], components[-1]
    example = example.replace('～', word)
    occurences = {}
    for form in wordForms:
        while form in example:
            index = example.index(form)
            example = example[:index] + '{}' + example[index + len(form):]
            occurences[index] = form
    occurences = [occurences[i] for i in sorted(occurences)]
    return { 'example': example, 'occurences': occurences, 'translation': translation }

def parseMeaning(entry):
    entry = re.sub(r'【[^】]+】( ；)?', '', entry)
    explanation = []
    index, counter = 0, 0
    while index < len(entry):
        if entry[index] == '（':
            counter += 1
            if counter == 1:
                startIndex = index
                hasKana = False
        elif entry[index] == '）':
            if counter == 0:
                entry = entry[:index] + entry[index + 1:]
                continue
            counter -= 1
            if counter == 0 and hasKana:
                explanation.append(entry[startIndex + 1 : index])
                entry = entry[:startIndex] + entry[index + 1:]
                index = startIndex - 1
        elif entry[index] in Hiraganas or entry[index] in Katakanas:
            hasKana = True
        index += 1
    return {
        'meaning': entry,
        'explanation': '；'.join(explanation),
        'examples': []
    }

def getWords(soup):
    words = []
    for div in soup.select('div.jp_word_comment'):
        try:
            word = str(div.select('span.jpword')[0].string).strip()
            if word in ['{word}']: continue
            kana = parseKana(''.join(str(element.string) for element in div.select('span.trs_jp')))
            wordTypes = []

            if len(div.select('div.tip_content_item')) > 0:
                for types in div.select('div.tip_content_item'):
                    wordTypes += parseWordType(str(types.string))
                wordTypes = list(set(wordTypes))
                forms = getForms(word, kana, wordTypes)
                meanings = []
                for entry in div.select('ul.jp_definition_com li.flag'):
                    meaningSpan = (entry.select('span.word_comment') or entry.select('span.jp_explain'))[0]
                    meaning = parseMeaning(parseEntry(str(meaningSpan.string)))
                    meanings.append(meaning)
                    if len(entry.select('div')) == 1: continue
                    example = ''
                    for element in entry.select('div')[1].children:
                        if isinstance(element, bs4.NavigableString):
                            example += str(element)
                        elif element.name == 'b':
                            for child in element.children:
                                if isinstance(element, bs4.NavigableString):
                                    example += str(element)
                                else:
                                    example += str(element.string)
                        elif element.name == 'br':
                            meaning['examples'].append(parseExample(parseEntry(example), word, forms))
                            example = ''

            else:
                explainString = ''
                for child in div.select('span.jp_explain')[0].children:
                    if isinstance(child, bs4.NavigableString):
                        explainString += str(child).strip() + '\n'
                wordTypes = []
                for match in re.findall(r'【[^】]+】', explainString):
                    wordTypes += parseWordType(match)
                    explainString = explainString.replace(match, '')
                wordTypes = list(set(wordTypes))
                forms = getForms(word, kana, wordTypes)
                meanings = []
                for entry in re.split(r'\r*\n*\u3000*', explainString):
                    entry = parseEntry(entry)
                    if entry == '':
                        continue
                    if '／' in entry:
                        meanings[-1]['examples'].append(parseExample(entry, word, forms))
                    else:
                        entry = re.sub(r'（[0-9]+）', '', entry)
                        meanings.append(parseMeaning(entry))

        except Exception as e:
            continue
        words.append({
            'word': word,
            'kana': kana,
            'wordTypes': wordTypes,
            'meanings': meanings,
        })
    return words

def getHJDictionaryURL(word):
    return 'http://dict.hjenglish.com/jp/jc/{}'.format(urllib.parse.quote(word))

def getContentFromURL(url):
    return urllib.request.urlopen(url).read()

def getSoupFromHJDictionary(word):
    return bs4.BeautifulSoup(getContentFromURL(getHJDictionaryURL(word)))

def search(word):
    soup = getSoupFromHJDictionary(word)
    if len(soup.select('#divTryCJ')) == 0:
        words = getWords(soup)
    else:
        words = []
        suggestions = soup.select('#vagueWord')[0].nextSibling.nextSibling
        if suggestions.name == 'ul':
            for child in suggestions.children:
                if child.name == 'li':
                    for anchor in child.select('a'):
                        words += search(str(anchor.string))
    return words

def printWord(word):
    print('{} - {} （{}）'.format(word['word'], word['kana'], '，'.join(word['wordTypes'])))
    for index, meaning in enumerate(word['meanings']):
        print('{}. {} - {}'.format(index + 1, meaning['meaning'], meaning['explanation']))
        for example in meaning['examples']:
            print('    {} - {}'.format(example['example'].format(*['[' + o + ']' for o in example['occurences']]), example['translation']))
            if len(example['occurences']) == 0:
                print('    Warning: This example has no occurences.')

def searchLoop():
    try:
        while True:
            for word in search(input('Search: ')):
                printWord(word)
                print()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    #[printWord(w) for w in getWords(bs4.BeautifulSoup(open('aru.html').read()))]
    searchLoop()


