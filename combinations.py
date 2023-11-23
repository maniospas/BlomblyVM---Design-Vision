def func(x):
    return x*3


class Machine:
    def __init__(self, ops, memory):
        ops = {"end": "builtin", "lazy": "builtin", "return": "builtin", "call": "builtin", "is": "builtin", "input": "builtin"} | ops
        self._ops = ops
        self._op2id = {op: i for i, op in enumerate(ops)}
        self._id2op = {i: op for i, op in enumerate(ops)}
        self._memsize = memory+1
        self._numops = len(ops)
        self._none = memory-1
        self._end_statement = self._hash(("end", "none"))  # used for feedforward search of fun endings

    def _hash(self, command):
        op = command[0]
        if op not in self._op2id:
            raise Exception(f"Invalid command {op}")
        ret = self._op2id[op]
        mul = self._numops
        for arg in command[1:]:
            if arg == "none":
                arg = self._none
            ret += mul*(arg+1)
            mul *= self._memsize
        return ret

    def _unhash(self, command):
        args = [self._id2op[command % self._numops]]
        command = int(command/self._numops)
        while command > 0:
            args.append(command % self._memsize-1)
            command = int(command / self._memsize)
        return args

    def compile(self, commands):
        return [self._hash(command) for command in commands]

    def compress(self, commands):
        return ";".join(hex(command) for command in self.compile(commands))

    def execute(self, compiled, memory=None, pos=0, end=None, copy=True, top=None):
        if isinstance(compiled, str):
            compiled, memory = parse(compiled)
            compiled = self.compile(compiled)
        if memory is None:
            memory = []
        if copy:
            _memory = [None for _ in range(self._memsize)]
            if memory is not None:
                for i in range(len(memory)):
                    _memory[i] = memory[i]
        else:
            _memory = memory
        if end is None:
            end = len(compiled)-1
        if top is None:
            top = memory
        while pos <= end:
            command = compiled[pos]
            command = self._unhash(command)
            if command[0] == "input":
                result = top[command[2]]  # specifically from parent memory
            elif command[0] == "is":
                result = _memory[command[2]]
                if isinstance(result, list):
                    result = self.execute(compiled, _memory, pos=result[0], end=result[1], copy=False, top=top)
            elif command[0] == "call":
                if len(command) > 3:
                    args = _memory[command[2]]
                    fun = _memory[command[3]]
                else:
                    args = "none"
                    fun = _memory[command[2]]
                pushed_memory = [mem for mem in _memory]
                if args == "none":
                    result = None
                else:
                    result = self.execute(compiled, pushed_memory, pos=args[0], end=args[1], copy=False, top=top)
                if result is not None:
                    raise Exception("First argument of a call should not return a value")
                result = self.execute(compiled, pushed_memory, pos=fun[0], end=fun[1], copy=False, top=top)
            elif command[0] == "end":
                return None
                #raise Exception("Reached the end of lazy code without returning")
            elif command[0] == "lazy":
                fend = pos+1
                depth = 0
                while fend < len(compiled):
                    if self._id2op[compiled[fend] % self._numops] == "lazy":
                        depth += 1
                    if compiled[fend] == self._end_statement and depth == 0:
                        break
                    if compiled[fend] == self._end_statement:
                        depth -= 1
                    fend += 1
                if end == len(compiled):
                    raise Exception("Lazy code definition never ended")
                result = (pos+1, fend)
                pos = fend
            elif command[0] == "return":
                return _memory[command[2]]
            else:
                op = self._ops[command[0]]
                args = [_memory[arg] for arg in command[2:]]
                result = op(*args)
            if command[1] != self._none:
                _memory[command[1]] = result
            pos += 1


def parse(text):
    program = list()
    symbols = dict()
    memory = list()
    parent_symbols = dict()
    text = text.replace("{", "lazy();").replace("}", "end();")

    def get(symbol, allow_new=True):
        symbol = symbol.strip()
        if symbol == "none":
            return symbol
        if symbol.isdigit():
            repr = " "+symbol
            if repr not in parent_symbols:
                parent_symbols[repr] = len(symbols)
                program.append(["input", parent_symbols[repr], len(memory)])
                memory.append(int(symbol))
            return parent_symbols[repr]
        if symbol[0] == "#" and symbol[1:].isdigit():
            return int(symbol[1:])
        if symbol not in symbols:
            if not allow_new:
                raise Exception(f"Symbol not declared before first occurance: {symbol}")
            symbols[symbol] = len(symbols)
        return symbols[symbol]

    text = "\n".join([line.split("//")[0] for line in text.split("\n")])  # remove line comments

    for line in text.split(";"):
        line = line.strip()
        if not line:
            continue
        eq = line.split("=")
        if len(eq) == 1:
            eq = ["none"] + eq
        rhs = eq[1].split("(")
        op = rhs[0].strip()
        if len(rhs) == 1:
            args = []
        else:
            args = [get(arg, False) for arg in rhs[1][:-1].split(",") if arg.strip()]
        if op in symbols:
            program.append(["call", get(eq[0])]+args+[get(op)])
            continue
        program.append([op, get(eq[0])]+args)
    return program, memory

operations = {
    "add": lambda x, y: x + y,
    "sub": lambda x, y: x - y,
    "print": print
}
with open("test.mm") as file:
    program = file.read()

program, memory = parse(program)
#print("\n".join([" ".join([command[0].ljust(7)]+[str(arg).ljust(4) for arg in command[1:]]) for command in program]))
machine = Machine(operations, 32)
compiled = machine.compile(program)
machine.execute(compiled, memory)
