def array_join(array, glue, func):
    if len(array) == 0:
        return ''
    res = ''
    for element in array:
        res += func(element) + glue
    res = res[:-len(glue)]
    return res
