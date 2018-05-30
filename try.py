from buildpg import render, MultipleValues, Values


sql, params = render('SELECT {{ v }} FROM', v=1)
debug(sql, params)

sql, params = render('SELECT {{ v }} FROM {{ d }} {{ e }}', v=Values(1, 2, 3), d=213, e=321)
debug(sql, params)


sql, params = render('SELECT {{ v }} FROM', v=MultipleValues(Values(1, 2, 3), Values('a', 'b', 'c')))
debug(sql, params)
