import copy
from collections import Counter
from scipy.spatial import distance

def calcInitCent(X):
    distArr = []
    for i in range(len(X)):
        dis = 0
        for k in range(len(X)):
            dis += distance.cosine(X[i], X[k])
        distArr.append(dis)
    return  min((val, idx) for (idx, val) in enumerate(distArr))


def calcCentClast(X, labArr):
    labeDict = dict(Counter(labArr))
    for it in labeDict:
        labeDict[it] = [[],[]]
    for i in range(len(labArr)):
        dis = 0
        for k in range(len(labArr)):
            if labArr[i] == labArr[k]:
                dis += distance.cosine(X[i], X[k])
        labeDict[labArr[i]][0].append(i)
        labeDict[labArr[i]][1].append(dis)
    optPoints = []
    print(labeDict)
    for it in labeDict:
        val, ind = min((val, idx) for (idx, val) in enumerate(labeDict[it][1]))
        optPoints.append(labeDict[it][0][ind])
    return optPoints


def labalesXl(X, C):
    labalesArr = []
    for i in range(len(X)):
        mDist = 10000000000000
        knum = None
        for it in C:
            kd = distance.cosine(X[i], X[it])
            if kd < mDist:
                mDist = kd
                knum = it
        labalesArr.append(knum)
    return labalesArr

def probAdvSlov(X, C):
    lab = labales(X, C)
    counter = Counter(lab)
    print(list(counter))


def probTrSloving(X, C):
    funVal = 0
    for i in range(len(X)):
        mDist = 10000000000000
        for it in C:
            kd = distance.cosine(X[i], X[it])
            if kd < mDist:
                mDist = kd
        funVal += mDist
    return funVal


def calcCentB2(X, B2):
    distArr = []
    for it in B2:
        dis = 0
        for kit in B2:
            dis += distance.cosine(X[it], X[kit])
        distArr.append(dis)
    return  min((val, idx) for (idx, val) in enumerate(distArr))


def takeSubSetS2(C, X):
    return list(set([i for i in range(len(X))]) - set(C))


def takeSubSetB2WithPoint(C, X, P):
    B2 = []
    for i in range(len(X)):
        tDist = distance.cosine(X[P], X[i])
        mDist = 100000000000000
        for it in C:
            kd = distance.cosine(X[i], X[it])
            if kd < mDist:
                mDist = kd
        if tDist < mDist:
            B2.append(i)
    return B2


def ZForPointCl(C, X, P):
    zdisVal = 0
    for i in range(len(X)):
        tDist = distance.cosine(X[P], X[i])
        mDist = 10000000000000
        for it in C:
            kd = distance.cosine(X[i], X[it])
            if kd < mDist:
                mDist = kd
        if (tDist - kd) > 0:
            zdisVal += tDist - kd
    zdisVal = (1 / len(X)) * zdisVal
    return zdisVal


def SMGKM(X, N):
    C = []
    for i in range(N):
        if i == 0:
           val, ind =  calcInitCent(X)
           C.append(ind)
        else:
            S2 = takeSubSetS2(C, X)
            zPoints = []
            B2PointsCentsrs = []
            for it in S2:
                B2 = takeSubSetB2WithPoint(C, X, it)
                val, cp = calcCentB2(X, B2)
                B2PointsCentsrs.append(B2[cp])
                zVal = ZForPointCl(C, X, cp)
                zPoints.append(zVal)
            vl, ind = max((val, idx) for (idx, val) in enumerate(zPoints))
            X3 = []
            for i in range(len(B2PointsCentsrs)):
                if zPoints[i] >= vl:
                    X3.append(B2PointsCentsrs[i])
            counter = Counter(X3)
            X3 = list(counter)
            slovingArr = []
            for it in X3:
                CNow = copy.copy(C)
                CNow.append(it)
                labArr = labalesXl(X, CNow)
                calck = calcCentClast(X, labArr)
                slovingArr.append(calck)
            probArr = []
            for it in slovingArr:
                probArr.append(probTrSloving(X, it))
            vlP, indP = max((val, idx) for (idx, val) in enumerate(probArr))
            C = slovingArr[indP]
    return C