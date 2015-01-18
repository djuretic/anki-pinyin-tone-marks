# -*- coding: utf-8 -*-
from anki.hooks import addHook
from aqt import mw
import re

PinyinToneMark = {
    0: u"aoeiuv\u00fc",
    1: u"\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6",
    2: u"\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8",
    3: u"\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da",
    4: u"\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc",
}


# based on http://stackoverflow.com/a/8200388
def decode_pinyin(s):
    s = s.lower()
    r = ""
    t = ""
    for c in s:
        if c in ''.join(PinyinToneMark.values()) or c == ' ':
            t += c
        elif c >= 'a' and c <= 'z':
            t += c
        elif c == ':':
            # assert t[-1] == 'u'
            t = t[:-1] + u"\u00fc"
        else:
            if c >= '0' and c <= '5':
                tone = int(c) % 5
                if tone != 0:
                    m = re.search(u"[aoeiuv\u00fc]+", t)
                    if m is None:
                        t += c
                    elif len(m.group(0)) == 1:
                        t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                    else:
                        if 'a' in t:
                            t = t.replace("a", PinyinToneMark[tone][0])
                        elif 'o' in t:
                            t = t.replace("o", PinyinToneMark[tone][1])
                        elif 'e' in t:
                            t = t.replace("e", PinyinToneMark[tone][2])
                        elif t.endswith("ui"):
                            t = t.replace("i", PinyinToneMark[tone][3])
                        elif t.endswith("iu"):
                            t = t.replace("u", PinyinToneMark[tone][4])
                        else:
                            t += "!"
            r += t
            t = ""
    r += t
    return r


# Change tone numbers with tone marks on pinyin fields
def onFocusLost(flag, note, field):
    if "hanzi" not in note.model()['name'].lower():
        return flag
    for c, name in enumerate(mw.col.models.fieldNames(note.model())):
        if c != field:
            continue
        if 'pinyin' not in name.lower():
            continue

        srcTxt = mw.col.media.strip(note[name])
        if not srcTxt:
            return flag
        updatedValue = decode_pinyin(note[name])
        if updatedValue != srcTxt:
            note[name] = updatedValue
            note.flush()
            return True
    return flag


addHook('editFocusLost', onFocusLost)
