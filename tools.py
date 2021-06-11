"""Help functions"""


def array_join(array, glue, func):
    """
    Join list wit separated and apply function to each element

    :param list array: List of pieces
    :param string glue: Delimiter
    :param function func: Apply function to each element

    :return: joined string
    :rtype: string
    """
    if len(array) == 0:
        return ''
    res = ''
    for element in array:
        res += func(element) + glue
    res = res[:-len(glue)]
    return res
