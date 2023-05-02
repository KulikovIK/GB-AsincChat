import dis


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = []
        for func in clsdict:
            try:
                res = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for el in res:
                    if el.opname == 'LOAD_GLOBAL':
                        if el.argval not in methods:
                            methods.append(el.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError(
                    f'В классе Client обнаружено использование запрещенного метода - {command}')
        if 'parse_response' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError(
                'Отсутствуют вызовы функций, работающих с сокетами.')
        super.__init__(clsname, bases, clsdict)
