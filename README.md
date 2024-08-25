# Metamorph
Implements metamorphism for Python classes using decorators

## Aim
Metamorphic classes are similar to polymorphic classes except that the sub-class is applied to an already existing object. 

## Example usage
```python
from metamorph import morph, Metamorphic

class MetamorphBase(Metamorphic) :
    def greet(self) :
        return "Hello, World!"

class MetamorphChild(MetamorphBase) :
    def greet(self) :
        return "Hello, Earth!"

greeter = MetamorphBase()
print(greeter.greet()) # prints Hello, World!
morph(greeter, MetamorphChild)
print(greeter.greet()) # prints Hello, Earth!
```

## Constraints
By default the module enforces a number of constraints on metamorph children. It throws exception when the class is created. This is designed to prevent unexpected behavior during runtime. These can be partially or wholly ignored using `metamorph_config`. (See below)


To avoid unpredictable side effects child classes are meant only to change the behavior of an object without containing local state. Thus they can only implement methods that already exist in the metamorph base and function signatures must match. Implementing `__init__` or `__new__` or any attributes also throws an exception In addition child classes can only inherit directly from the base class and it multiple inheritance is forbidden. The base class is still allowed to use multiple inheritance.

## Configuration
The module can be configured by calling `metamorph_config`. The following options are available

| Option | Default | Notes |
----------------------------
| `strict` | True | Setting this to False bypasses all checks on the sanity of the code.
| allow_mixed_typing | False | Allows child metamorph to use type hinting if not applied by the base. However changing or removing the hint still raises an error.
| allow_init | False | Allows `__init__` or `__new__` to be defined in the child classes
| private_members | False | Normally members starting with __ are shared between the base and its children. Setting this option to true makes these variables only accessible from the base class.

## API

* Metamorphic - The base class for metamorphic classes
* metamorph_config(strict, allow_mixed_types, allow_init, private_members) - Used to configure the module
* morph(obj, morphclass) - Morphs obj to the given morphclass
* isMetamorphic(obj_or_cls) - Returns if class or object instance are metamorphic
* isMetamorphicBase(obj_or_cls) - Returns if class or object instance is a metamorphic base class
* isMetamorphicChild(obj_or_cls) - Returns if class or object instance is a metamorphic child class
* MetamorphicType - The metaclass for metamorphic classes. You should not need to use it directly. Inherit from the Metamorphic class instead. 