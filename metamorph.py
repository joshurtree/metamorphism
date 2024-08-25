from dataclasses import dataclass
from importlib import import_module
from inspect import getmembers, isfunction, Parameter, signature, Signature
import re
from types import MethodType, new_class
from typing import Any, Callable, MutableMapping

@dataclass
class MetamorphError(BaseException) :
    message: str

@dataclass
class MetamorphException(Exception) :
    message: str

@dataclass
class _MetamorphConfig :
    strict: bool = True
    allow_mixed_typing: bool = False
    allow_init: bool = False
    private_members: bool = False

_config = _MetamorphConfig()

def metamorph_config(    
    strict: bool = True,
    allow_mixed_typing: bool = False,
    allow_init: bool = False,
    private_members: bool = False
) :
    _config = _MetamorphConfig(strict, 
                               allow_mixed_typing, 
                               allow_init, 
                               private_members)

class MetamorphicType(type) :
    def __new__(metacls, classname, bases, namespace, **kwargs) :
        cls = super().__new__(metacls, classname, bases, namespace)
        
        if classname != "Metamorphic" and classname != "Metamorphi":
            if Metamorphic in cls.__bases__ :                
                cls.__metamorph_of__ = cls
            else :
                _checkMetamorphChild(cls, bases)
                cls.__metamorph_of__ = cls.__base__

        return cls
    
class Metamorphic(metaclass=MetamorphicType) :
    def __getattribute__(self, attrname) :
        getAttribute = lambda name : super(Metamorphic, self).__getattribute__(name)

        if _config.private_members or not re.match("_\w+?_\w+$") :
            return getAttribute(attrname)
        
        classname = getAttribute("__class__").__name__
        basename = getAttribute("__metamorph_of__").__name__

        return getAttribute(re.sub("^_" + classname + "__", 
                               "_" + basename + "__",
                               attrname))
        

def isMetamorphic(obj_or_cls) :
    return isinstance(obj_or_cls, (Metamorphic, MetamorphicType))

def isMetamorphicBase(obj_or_cls) :
    if not isMetamorphic(obj_or_cls) :
        return False
    
    if isinstance(obj_or_cls, MetamorphicType) :
        return Metamorphic in obj_or_cls.__bases__  
    else : 
        return Metamorphic in type(obj_or_cls).__bases__

def isMetamorphicChild(obj_or_cls) :
    return isMetamorphic(obj_or_cls) and not isMetamorphicBase(obj_or_cls)

def _checkMetamorphChild(cls, bases) :
    if _config.strict :
        if len(bases) > 1 :
            raise MetamorphError("Metamorph child cannot have any other base classes")
        
        if Metamorphic not in bases[0].__bases__ :
            raise MetamorphError("Cannot subclass a metamorph child")
        
        base = bases[0]

        if "__annotations__" in cls.__dict__:
            raise MetamorphError("Metamorph class cannot contain annotations")

        for name, attr in getmembers(cls, lambda f : isfunction(f)) :
            if name in vars(cls):
                _checkFunction(attr, base)

def _signaturesMatch(a: Callable, b: Callable, loose: bool = False) -> bool :
    asig = signature(a)
    bsig = signature(b)

    aparams = asig.parameters
    bparams = bsig.parameters
    
    annotationsMatch = lambda a, b : a == Parameter.empty or a == b if loose else a == b
    tests = [
        len(aparams) == len(bparams),
        annotationsMatch(asig.return_annotation, bsig.return_annotation)
    ]

    positional =  [Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD]
    tests += [a == b for a, b in zip(aparams, bparams) if aparams[a].kind in positional]

    paramTest = lambda a, b : annotationsMatch(a.annotation, b.annotation) and a.kind == b.kind
    tests += [paramTest(aparams[name], bparams[name]) for name in aparams]

    return all(tests)

def _checkFunction(func, target) :
    createException = lambda err : MetamorphError(
        f"The function {func.__qualname__} {err} of {target.__name__}"
    )

    if not _config.allow_init and func.__name__ in ["__init__", "__new__"] :
        raise MetamorphError(f"The function {func.__name__} is not allowed in metamorph class (Set allow_init to True to prevent this error)") 
    
    if func.__name__ not in dir(target) :
        raise createException("is not a member")

    targetFunc = getattr(target, func.__name__)
    if not callable(targetFunc) :
        raise createException("is not a callable member")
    
    if not _signaturesMatch(targetFunc, func, _config.allow_mixed_typing) : 
        raise createException("signature does not match function") 

def morph(obj, morphclass) :
    if not isMetamorphic(obj) :
        raise MetamorphException("Object is not metamorphic")
    
    if not isMetamorphic(morphclass) :
        raise MetamorphException("Morph is not metamorphic")
    
    if morphclass.__metamorph_of__ != obj.__metamorph_of__ :
        raise MetamorphException("Object and morph do not belong to the same morphic")
    
    obj.__class__ = morphclass