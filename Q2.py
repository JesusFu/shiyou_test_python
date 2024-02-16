'''
@陈方熠
'''
def replaceLetter(s: str, k: int) -> str:
    if k <= 0:
        return s

    res = ''

    for index, c in enumerate(s):
        if index < k:
            start_point = 0
        else:
            start_point = index - k
        end_point = index

        if c in s[start_point:end_point]:
            res += '-'
        else:
            res += c

    return res

def test():
    assert replaceLetter('abcdefaxc', 10) == 'abcdef-x-'
    assert replaceLetter('abcdefaxcqwertba', 10) == 'abcdef-x-qw-rtb-'
    assert replaceLetter('a', 10) == 'a'
    assert replaceLetter('', 5) == ''
    assert replaceLetter('aabcdef', 0) == 'aabcdef'
    assert replaceLetter('aabcdef', -1) == 'aabcdef'
    assert replaceLetter('abcdef', 10) == 'abcdef'

if __name__ == '__main__':
    # test()

    s = input().strip()
    k = int(input().strip())
    print(replaceLetter(s, k))
