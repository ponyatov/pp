# object FORTH works over Marvin Minsky's frame model

import os,sys,time,re,pickle

# base generic unitree object = frame
# can act as any type wrapper, vector/stack, dict/map/vocabulary = slots

class Object:
    
    def __init__(self,V):
        # type/class tag, required for PLY parser library
        self.type  = self.__class__.__name__.lower()
        # signel value for primitive types from implementation language 
        self.value = V
        # slots = associative array keys
        self.attr  = {}
        # vector = stack = subtrees
        self.nest  = []

    # unitree operations 

    # frame[key] = obj            
    def __setitem__(self,key,obj):
        self.attr[key] = obj
    # frame[key]
    def __getitem__(self,key):
        return self.attr[key]
        
    # treat nest as stack
    
    # frame << obj
    def __lshift__(self,obj):
        return self.push(obj)
    # push as stack
    def push(self,obj):
        self.nest.append(obj) ; return self
    # pop as stack
    def pop(self):
        return self.nest.pop()
    # top element
    def top(self):
        return self.nest[-1]
    def dropall(self):
        self.nest = []
    # classical stack ops
    def dup(self): self.push(self.top()) ; return self
    def drop(self): self.nest.pop() ; return self
    def swap(self):
        B = self.pop(); A = self.pop();
        self.push(B) ; self.push(A)
        return self
    
    # dumping
    
    def __repr__(self):
        return self.dump()
    dumped = []
    def dump(self,depth=0,prefix=''):
        S = self.pad(depth) + self.head(prefix)
        if not depth: Object.dumped = []
        if self in Object.dumped: return S + '...'
        Object.dumped.append(self)
        for i in self.attr:
            S += self.attr[i].dump(depth+1,prefix='%s = '%i)
        for j in self.nest:
            S += j.dump(depth+1)
        return S
    def head(self,prefix=''):
        return '%s<%s:%s>'%(prefix,self.type,self.value)
    def pad(self,N):
        return '\n'+'    '*N
    
class Primitive(Object): pass

class Symbol(Primitive): pass

class Number(Primitive):
    def __init__(self,N):
        Primitive.__init__(self, float(N))
    # math
    def add(self,obj):
        if isinstance(obj,Number):
            return Number(self.value + obj.value)
        else:
            raise SyntaxError(obj)
        
class String(Primitive): pass

class Container(Object): pass

class Stack(Object): pass

class Map(Container):
    def __lshift__(self,F):
        self.attr[F.__name__] = Fn(F)
    def push(self,obj):
        self.attr[obj.value] = obj
        
class Active(Object): pass

class Fn(Active):
    def __init__(self,F):
        Active.__init__(self, F.__name__)
        self.fn = F
    def __call__(self):
        self.fn()

S = Stack('data')

W = Map('vocabulary')

W['W'] = W
W['S'] = S

def q():
    print S.pop()
W['?'] = Fn(q)

def DROPALL(): S.dropall()
W['.'] = Fn(DROPALL)
W << DROPALL

def BYE(): sys.exit(0)
W << BYE

def ADD():
    B = S.pop() ; A = S.pop() ; S.push( A.add(B) )
W['+'] = Fn(ADD)

# << ( frame obj -- frame ) push to frame
def PUSH():
    obj = S.pop() ; S.top() .push( obj )
W << PUSH
W['<<'] = Fn(PUSH)

# >> ( frame -- frame obj ) pop from frame
def POP():
    S.push( S.top().pop() )
W << POP
W['>>'] = Fn(POP)

# ! ( frame slot obj -- frame ) set slot value
def ST():
    obj = S.pop() ; slot = S.pop()
    S.top()[slot.value] = obj
W << ST    
W['!'] = Fn(ST)

# @ ( frame slot -- frame value | frame ) fetch slot value
def LD():
    slot = S.pop()
    try: S.push ( S.top()[slot.value] )
    except KeyError: pass
W << LD    
W['@'] = Fn(LD)

def DUP(): S.dup()
W << DUP

def DROP(): S.drop()
W << DROP

def SWAP(): S.swap()
W << SWAP

def OVER(): S.over()

import ply.lex as lex

tokens = ['symbol','number']

t_ignore = ' \t\r\n'

def t_number(t):
    r'[\+\-]?[0-9]+(\.[0-9]*)?([eE][\+\-][0-9]+)?'
    return Number(t.value)
    
def t_symbol(t):
    r'[0-9a-zA-Z_\.\?\+\-\@\!\:\;\<\>]+'
    return Symbol(t.value)

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()

# WORD ( -- obj:token ) get next token from source code stream
def WORD():
    token = lexer.token()
    if token: S << token
    return token
W << WORD

# FIND ( token -- callable ) lookup in vocabulary
def FIND():
    token = S.pop()
    try:
        S.push( W[token.value] ) ; return True
    except KeyError:
        try:
            S.push( W[token.value.upper()] ) ; return True
        except KeyError:
            S.push(token) ; return False
    
# EXECUTE ( callable -- ) run callable
def EXECUTE():
    if callable(S.top()): S.pop() ()

# INTERPET ( str -- ) interpret string
def INTERPRET():
    lexer.input(S.pop().value)
    while True:
        if not WORD(): break
        if isinstance(S.top(),Symbol):
            if FIND(): EXECUTE()
W << INTERPRET

while True:
    print S
    try:
        S .push( String ( raw_input('\nbodik> ') )) ; INTERPRET()
    except EOFError:
        BYE()