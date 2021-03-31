cache = dict()

def similarity(word1 : str, word2 : str):
    if (word1, word2) in cache:
        return cache[(word1,word2)]
    if word1 == word2: return 0
    if not word1:
        return len(word2)
    elif not word2:
        return len(word1)
    check0 = similarity(word1[1:], word2[1:])
    if check0 == 0:
        cache[(word1,word2)] = 1
        return 1
    if word1[0] == word2[0]:
        cache[(word1,word2)] = check0
        return check0
    if check0 == max(len(word1[1:]),len(word2[1:])):
        cache[(word1,word2)] = 1 + check0
        return 1 + check0
    check1 = similarity(word1[1:], word2)
    if check1 < check0:
        cache[(word1,word2)] = 1 + check1
        return 1 + check1
    check2 = similarity(word1, word2[1:])
    if check2 < check0:
        cache[(word1,word2)] = 1 + check2
        return 1 + check2
    cache[(word1,word2)] = 1 + check0
    return 1 + check0