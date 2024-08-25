import unittest
from metamorph import *


class StrictBase(Metamorphic) :
    def __init__(self) -> None:
        self.__private = True

    def greet(self) :
        return "Hello, World!"
    
    def paramTest(self, a: str, b) :
        return False 
    
    def privateTest(self) :
        pass

class StrictTest(unittest.TestCase) :    
    def test_positive(self) :   
        class WorkingMorph(StrictBase) :
            def greet(self = None) :
                return "Hello, Earth!"

            def paramTest(self, a: str, b) :
                return True

            def privateTest(self) :
                return self.__private
                 
        a = StrictBase()

        self.assertEqual(a.greet(), "Hello, World!")
        self.assertFalse(a.paramTest("a", "b"))

        morph(a, WorkingMorph)

        self.assertEqual(a.greet(), "Hello, Earth!")
        self.assertTrue(a.paramTest("a", "b"))
        self.assertTrue(a.privateTest())

    def test_negative(self) :
        def typo_test() :
            class TypoMorph(StrictBase) :
                def geeet(self) :
                    print("Too many e's")
                
        self.assertRaises(MetamorphError, typo_test)

    def test_param_types(self) :
        def param_swap() :
            class SwapedParamsMorph(StrictBase) :
                def paramTest(self, b, a) :
                    return True
                    
        self.assertRaises(MetamorphError, param_swap)

class LooseBase(Metamorphic, strict=False) :
    pass

class LooseTest(unittest.TestCase) :
    def test_loose(self) :
        class SloppyMorph(LooseBase) :
            def greet(self) :
                return "Hello, World"

class LooseParamsBase(Metamorphic, allow_mixed_typing=True) :
    def __new__(cls, *args, **kargs) :
        obj = super(LooseParamsBase, cls).__new__(cls, *args, **kargs)
        return obj 
    
    def greet(self) :
        return "Hello, World!"
    
    def paramTest(self, a: str, b) :
        return False 

class LooseParamsTest(unittest.TestCase) :
    def test_param_types(self) :
        class LooseParamsMorph(LooseParamsBase) :
            def paramTest(self, a: str, b: str) :
                return True
                        
        a = LooseParamsBase()
        morph(a, LooseParamsMorph)
        self.assertTrue(a.paramTest("", ""))

if __name__ == "__main__" :
    unittest.main()