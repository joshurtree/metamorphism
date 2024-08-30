# Metamorphism
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
By default the module enforces a number of constraints on metamorph children. It throws exception when the class is created. This is designed to prevent unexpected behavior during runtime. These can be partially or wholly ignored using `CustomMetamorphc`. (See below)

To avoid unpredictable side effects by default child classes are only allowed to change the behavior of an object. They cannot maintain their own state. Thus they can only implement methods that already exist in the metamorphic class and method signatures must match. Implementing `__init__` or `__new__` or any attributes also throws an exception. In addition child classes can only inherit directly from the base class and multiple inheritance is forbidden. The base class is still allowed to use multiple inheritance.

## Configuration
The module can be configured by using the metaclass `CustomMetamorphic` followed by keyword/option pairs. For example

```python
class UnsafeMetamorphic(Metamorphism, metaclass=CustomMetamorphism, strict=False) :
    pass

class UnsafeMetamorph(UnsafeMetamorphic) :
    def can_define_anything(self) :
        pass
```
If you want to use the same settings in several metamorphic classes then create a class which derives from the `MetamorphismBase` class. For Example
```python
class UnsafeMetamophism(MetamorphismBase, metaclass=CustomMetamorphism, strict=False) :
    pass

class UnsafeMetamorphic(UnsafeMetamophism) :
    pass

class AnotherMetamorphic(UnsafeMetamophism) :
    pass
```

The following options are available
| Option | Default | Notes |
|:-------|:--------|:------|
| `strict` | True | Setting this to False bypasses all checks on the sanity of the code. Note: Due to the potential for unexpected side effects any bugs reported from using this option may not addressed.
| `allow_mixed_typing` | False | Allows child metamorph to use type hinting if not applied by the base. However changing or removing the hint still raises an error.
| `allow_init` | False | Allows `__init__` or `__new__` to be defined in the child classes
| `allow_metamorph_subclassing` | False | Allow classes to inherit from metamorphs.
| `private_members` | False | Normally members starting with __ are shared between the base and its children. Setting this option to true makes these variables only accessible from the base class.

## API

* `Metamorphic` - The base class for metamorphic classes.
* ~~`metamorphism_config(strict, allow_mixed_types, allow_init, private_members)` - Used to configure the module.~~ 
* `morph(obj, morphclass)` - Morphs obj to the given morphclass.
* `ismetamorphic(obj_or_cls)` - Returns if class or object are metamorphic.
* `ismetamorphicbase(obj_or_cls)` - Returns if class or object is a metamorphic base class.
* `ismetamorphicchild(obj_or_cls)` - Returns if class or object is a metamorphic child class.
* `ismetamorphicconfig(obj_or_cls)` - Returns if class or object is use to configure metamorphism 
* `MetamorphismError` - Raised if there is a problem with the definition of the classes.
* `MetamorphismException` - Raised if `morph` is used incorrectly.
* `MetamorphicType` - The metaclass for metamorphic classes. You should not need to use it directly. Inherit from the Metamorphic class instead.
* `CustomMetamorphic` - Allow customisation of metamorphism constraints.
* `MetamorphismBase` - The base class used for all metamorphism.