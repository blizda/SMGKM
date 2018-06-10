import math
import re
import pymorphy2
from chardet import UniversalDetector
from os import listdir
from os.path import join, basename, isdir
import numpy as np


class SubsReader:
    def __init__(self, fileName, morph):
        self.__fileName = fileName
        self.__morph = morph
        self.__dockDict = None
        self.__wordQvant = 0
        self.__tf = None
        self.__normName = None

    def __fileEncoding__(self, filename):
        detector = UniversalDetector()
        with open(filename, 'rb') as fh:
            for line in fh:
                detector.feed(line)
                if detector.done:
                    break
        detector.close()
        return detector.result['encoding']

    def __cleaningLine__(self, line):
        clearLine = re.sub('icq#\d+|#+|\{\\a6\}|\{\\an8\}'
                           '|<i>|</i>|\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+'
                           '|\n+|\r+|^\d+|^\.+$|\{\\fad\d+\}|\*+|<b>', '', line)
        if clearLine and clearLine != ' ':
            clearLine = re.sub('https?:\/\/.*[\r\n]*', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('www\.\w+\.\w+', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('\w+\.ru', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('([a-z0-9_-]+\.)*[a-z0-9_-]+@[a-z0-9_-]+'
                               '(\.[a-z0-9_-]+)*\.[a-z]{2,6}', '', clearLine, flags=re.MULTILINE)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=#\d+\w+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('\s*-\s|\s-\s*', ' ', clearLine)
            clearLine = re.sub('\.\.+|^\.\.+', '...', clearLine)
            clearLine = re.sub('\.\.\.$|\?!|!\?|\.{3}\?|\.{3}!', '.', clearLine)
            clearLine = re.sub('^\.+$|<i>', '', clearLine)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=#\d+\w+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('"|\[|\]|\(|\)|<font color=\w+\d+>|</font>|/|<font color=#\d+>', '', clearLine)
            clearLine = re.sub('♪', '', clearLine)
            clearLine = re.sub('♪', '', clearLine)
            clearLine = re.sub('\{\\a6\}|\{\\fad\d+\}', '', clearLine)
            clearLine = re.sub('\$+', '', clearLine)
            clearLine = re.sub('%+', '', clearLine)
            clearLine = re.sub('\^+', '', clearLine)
            clearLine = re.sub('@+', '', clearLine)
            clearLine = re.sub('«+', '', clearLine)
            clearLine = clearLine.strip()
            return clearLine
        return ''

    def __cleaningWord__(self, word):
        word = (re.sub('[\.\?!,:]|#|\{\\an8\}|\.{3}|', '', word)).strip()
        word = (re.sub('{\\a6\}', '', word)).strip()
        word = (re.sub('…|^–|–$', '', word)).strip()
        word = (re.sub('^–+', '', word)).strip()
        word = (re.sub('-+$', '', word)).strip()
        word = (re.sub('»+', '', word)).strip()
        word = (re.sub('«+ ', '', word)).strip()
        word = (re.sub('^-+', '', word)).strip()
        word = (re.sub('–+$', '', word)).strip()
        return word

    def __cleanWord__(self, word, morph):
        word =  self.__cleaningWord__(word)
        if word:
            return self.__morphParseWithPyMorphy__(morph, word.lower())


    def __morphParseWithPyMorphy__(self, morph, word):
        p = morph.parse(word)[0]
        normiliseWord = p.normal_form
        return normiliseWord

    def __cleanWordWithTags__(self, word, arr, morph):
        word = self.__cleaningWord__(word)
        if word:
            arr.append(self.__morphParseWithPyMorphy__(morph, word.lower()))
        return arr

    def __makeDockDict__(self, fileName, morph):
        with open(fileName, encoding=self.__fileEncoding__(fileName), errors='ignore') as file:
            wordDict = {}
            for line in file:
                clearLine = self.__cleaningLine__(line)
                if clearLine:
                    wordArray = clearLine.split()
                    for i in range(len(wordArray)):
                        word = self.__cleanWord__(wordArray[i], morph)
                        if word is not None:
                            if word in wordDict:
                                wordDict[word] = wordDict[word] + 1
                            else:
                                wordDict[word] = 1
                            self.__wordQvant += 1
        return wordDict

    def __makeTfDict__(self, dockDict, wordQv):
        tfDict = {}
        for it in dockDict:
            tfDict[it] = dockDict[it] / wordQv
        return tfDict

    @property
    def docDict(self):
        if self.__dockDict is None:
            self.__dockDict = \
                self.__makeDockDict__(self.__fileName, self.__morph)
        return self.__dockDict

    @property
    def tf(self):
        if self.__tf is None:
            self.__tf = \
                self.__makeTfDict__(self.docDict, self.__wordQvant)
        return self.__tf

    @property
    def name(self):
        if self.__normName is None:
            fn = self.__fileName.replace('.srt', '').replace('_', ' ')
            self.__normName = re.sub(r'[^\w\s]+', r' ', fn).strip()
        return self.__normName


class DocsRead:
    def __init__(self, wayToDocks, morph=None):
        self.__morph = morph
        if self.__morph is None:
            self.__morph = pymorphy2.MorphAnalyzer()
        self.__wayToDocks = wayToDocks
        self.__docList = None
        self.__allDict = None
        self.__termDoc = None
        self.__nameList = None
        self.__termDocDict = None

    def __readDocks__(self, wayToDocs):
        docDict = {}
        self.__nameList = []
        files = listdir(wayToDocs)
        for file in files:
            if file.endswith('.srt'):
                self.__serName = basename(join(wayToDocs, file)).replace('.srt', '').replace('_', ' ')
                norm = re.sub(r'[^\w\s]+', r' ', self.__serName).strip()
                docDict[norm] = SubsReader(join(wayToDocs, file), self.__morph)
                self.__nameList.append(norm)
        return docDict

    def __makeAllDict__(self, dockList):
        allDict = {}
        for it in dockList:
            for dit in dockList[it].docDict:
                if dit in allDict:
                    allDict[dit] = allDict[dit] + 1
                else:
                    allDict[dit] = 1
        return allDict

    def __termDocumentMatrix__(self, allDic, dockList):
        terFriqMatrix = []
        for tit in dockList:
            currentTf = dockList[tit].tf
            thisRes = []
            for it in allDic:
                if it in currentTf:
                    thisRes.append(currentTf[it] * math.log10(len(dockList) / allDic[it]))
                else:
                    thisRes.append(0)
            terFriqMatrix.append((np.array(thisRes, dtype=float) /
                                  np.linalg.norm(np.array(thisRes, dtype=float), ord=2)))
        return terFriqMatrix

    def __termDocumentMatrixDict__(self, allDic, dockList):
        terFriqMatrix = {}
        for tit in dockList:
            currentTf = dockList[tit].tf
            thisRes = []
            for it in allDic:
                if it in currentTf:
                    thisRes.append(currentTf[it] * math.log10(len(dockList) / allDic[it]))
                else:
                    thisRes.append(0)
            terFriqMatrix[dockList[tit].name] = ((np.array(thisRes, dtype=float) /
                                  np.linalg.norm(np.array(thisRes, dtype=float), ord=2)))
        return terFriqMatrix

    @property
    def docList(self):
        if self.__docList is None:
            self.__docList = \
                self.__readDocks__(self.__wayToDocks)
        return self.__docList

    @property
    def allDict(self):
        if self.__allDict is None:
            self.__allDict = \
                self.__makeAllDict__(self.docList)
        return self.__allDict

    @property
    def termDocMatrix(self):
        if self.__termDoc is None:
            self.__termDoc = \
                self.__termDocumentMatrix__(self.allDict, self.docList)
        return self.__termDoc

    @property
    def nameList(self):
        if self.__docList is None:
            self.__docList = \
                self.__readDocks__(self.__wayToDocks)
        return self.__nameList

    def termDocMatrixDict(self):
        if self.__termDocDict is None:
            self.__termDocDict = \
                self.__termDocumentMatrixDict__(self.allDict, self.docList)
        return self.__termDocDict