from dataclasses import dataclass
from inspect import getmembers, isfunction, Parameter, signature, Signature
import re
import types
from typing import Callable

@dataclass
class MetamorphismError(BaseException) :
    message: str

@dataclass
class MetamorphismException(Exception) :
    message: str

@dataclass
class _MetamorphismConfig :
    strict: bool = True
    allow_mixed_typing: bool = False
    allow_init: bool = False
    allow_metamorph_subclassing: bool = False
    private_members: bool = False

class MetamorphismBase :
    # Allow private variables to be shared between a metamorphic and is metamorph
    def __getattribute__(self, attrname) :
        getAttribute = lambda name : super(MetamorphismBase, self).__getattribute__(name)
        
        classname = getAttribute("__class__").__name__
        basename = getAttribute("__metamorph_of__").__name__

        private_attrname = re.sub("^_" + classname + "__", 
                            "_" + basename + "__",
                            attrname)
        return getAttribute(private_attrname)

class MetamorphicType(type) :
    config = _MetamorphismConfig()

    def __new__(metacls, classname, bases, namespace, **kwargs) :
        cls = super().__new__(metacls, classname, bases, namespace)

        if ismetamorphicbase(cls) :
            cls.__metamorph_of__ = cls
        elif ismetamorph(cls) :
            metacls._checkMetamorphChild(cls, bases, metacls.config)
            cls.__metamorph_of__ = cls.__base__.__metamorph_of__

        if not metacls.config.private_members :
            metacls.__getattribute__ = object.__getattribute__
        return cls

    def _checkMetamorphChild(cls, bases, config) :
        if config.strict :
            if len(bases) > 1 :
                raise MetamorphismError("Metamorph cannot have any base classes other than its metamorphic")
            
            base = bases[0]

            if not config.allow_metamorph_subclassing and ismetamorph(base) :
                raise MetamorphismError("Cannot subclass a metamorph")
            
            if "__annotations__" in cls.__dict__:
                raise MetamorphismError("Metamorph class cannot contain annotations")

            for name, attr in getmembers(cls, lambda f : isfunction(f)) :
                if name in vars(cls):
                    MetamorphicType._checkFunction(attr, base, config)

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

    def _checkFunction(func, target, config) :
        createException = lambda err : MetamorphismError(
            f"The function {func.__qualname__} {err} of {target.__name__}"
        )

        if not config.allow_init and func.__name__ in ["__init__", "__new__"] :
            raise MetamorphismError(f"The function {func.__name__} is not allowed in metamorph class (Set allow_init to True to prevent this error)") 
        
        if func.__name__ not in dir(target) :
            raise createException("is not a member")

        targetFunc = getattr(target, func.__name__)
        if not callable(targetFunc) :
            raise createException("is not a callable member")
        
        if not MetamorphicType._signaturesMatch(targetFunc, func, config.allow_mixed_typing) : 
            raise createException("signature does not match function") 

def _toclass(obj_or_cls) :
    return obj_or_cls if isinstance(obj_or_cls, MetamorphicType) else type(obj_or_cls)

def ismetamorphic(obj_or_cls) :
    return isinstance(_toclass(obj_or_cls), MetamorphicType)
 
def ismetamorphicconfig(obj_or_cls) :
    return _toclass(obj_or_cls).__base__ == MetamorphismBase

def ismetamorphicbase(obj_or_cls) :
    if not ismetamorphic(obj_or_cls) :
        return False
    
    return any(ismetamorphicconfig(cls) for cls in _toclass(obj_or_cls).__bases__)  

def ismetamorph(obj_or_cls) :
    return all([ismetamorphic(obj_or_cls), 
               not ismetamorphicbase(obj_or_cls), 
               not ismetamorphicconfig(obj_or_cls)])

def morph(obj, morphclass) :
    if not ismetamorphic(obj) :
        raise MetamorphismException("Object is not metamorphic")
    
    if not ismetamorphic(morphclass) :
        raise MetamorphismException("Morph is not metamorphic")
    
    if morphclass.__metamorph_of__ != obj.__metamorph_of__ :
        raise MetamorphismException("Object and morph do not belong to the same morphic")
    
    obj.__class__ = morphclass

def CustomMetamorphic(name, bases, attrs, **kwargs) :
    class CustomMetamorphicType(MetamorphicType) :
        config = _MetamorphismConfig(**kwargs)

    return CustomMetamorphicType(name, bases, attrs)
    #return types.new_class(name, bases=(MetamorphicBase, ), metaclass=CustomMetamorphicType)

class Metamorphic(MetamorphismBase, metaclass=MetamorphicType) :
    pass        
