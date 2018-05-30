from buildpg import render, MultipleValues, Values


class Test:
    def __invert__(self):
        print('invert')
        return self

    def __eq__(self, other):
        print('eq', other)
        return self

    def __ne__(self, other):
        print('ne', other)
        return self

    def __bool__(self):
        print('bool')
        return False


t = Test()
print(~t != 4)

# sql, params = render('SELECT {{ v }} FROM', v=1)
# debug(sql, params)
#
# sql, params = render('SELECT {{ v }} FROM {{ d }} {{ e }}', v=Values(1, 2, 3), d=213, e=321)
# debug(sql, params)
#
#
# sql, params = render('SELECT {{ v }} FROM', v=MultipleValues(Values(1, 2, 3), Values('a', 'b', 'c')))
# debug(sql, params)
