# Mocking using the Patch function

In this notebook I will share examples on how to do mocking on our unit tests using the `patch` function of the `unittest.mock` module.

I will also dedicate some lines to the relation of _**mocks**_ and _**scopes**_ for successfully mocking our targets

## Mocking the `len` BIF


```python
import unittest
from unittest.mock import patch


class Test(unittest.TestCase):
    @patch('__main__.len')  # I need to mock the len bif, so I patch it 
    def test_len(self, len_mock):
        len_mock.return_value = 0  # I need len to return 0 when it gets invoked
        self.assertEqual(len("six"), 0)  # not patched len of 'six' would return 3

unittest.main(argv=['.', 'Test'], exit=False)  # This is how you run unittests in notebooks ;)

```

    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.002s
    
    OK





    <unittest.main.TestProgram at 0x7f74b85e7908>



#### Explanation
Here I used `patch` as a decorator for `test_len`. The first param for patch is the path to the `target` to be mocked, in this example is `'__main__.len'`. 

What is `__main__`? that is the name of the module that IPhython created for this notebook. You can check the name of the module by exploring the `__name__` variable.


```python
print(__name__ == '__main__')  # This is True
```

    True


Patch created a MagicMock object that replaced the len function, this object was passed as an argument of `test_len`: `len_mock`. Then we assigned a return value for the mock to be returned when invoked. So for the lifespan of `test_len` any invocation to len will return 0 regardles of the invocation parameters.

## Identifying the target

It is very important to know **"what to mock"** and **"where the target lives"**, those two things will **identify the target**.

In terms of _what to mock_ you might want to mock an attribute of an object or maybe one of it's methods or any of it's members for that matter. Maybe you want to mock an entire class. You would decide that thinking on **"over what you need to have full control"** in your test.

Regarding _where the target lives_, first of all the target must be importable from the test module, if not you will potentially get either ModuleNotFoundError, AttributeError or ImportError and your test wont work. Secondly you need to **"patch where the object is used, NOT where its defined"**, this means that you'll have to identify where the target is being looked up, its containing scope. To be more precise, **the target is the object instance present in the containing scope of the artifact being tested, that it is going to be used by the artifact, and not the definition of the object**.

See examples one and two that ilustrates what I wrote before.

### Example 1


```python
from example_one import do_example_one


class TestExampleOne(unittest.TestCase):
    def test_do_example_one_no_mock(self):
        result = do_example_one()
        self.assertTrue(isinstance(result, int))

    # This mock is wrong, I'm mocking where get_random_natural is defined,
    # not where it is used
    @patch('randomizers.get_random_natural', new=lambda: 8)
    def test_do_example_one_bad_patch(self):
        result = do_example_one()
        self.assertEqual(result, 8)

    # This mock is good, I'm mocking where get_random_natural is used,
    # not where it is defined. Here I am mocking the instance of 
    # get_random_natural function loaded by the example_one module
    @patch('example_one.get_random_natural', new=lambda: 8)
    def test_do_example_one_good_patch(self):
        result = do_example_one()
        self.assertEqual(result, 8)

unittest.main(argv=['.', 'TestExampleOne', '-v'], exit=False)

```

    test_do_example_one_bad_patch (__main__.TestExampleOne) ... FAIL
    test_do_example_one_good_patch (__main__.TestExampleOne) ... ok
    test_do_example_one_no_mock (__main__.TestExampleOne) ... 

    
    I got 1434704449655547027
    
    I got 8
    
    I got 3348048791324072659


    ok
    
    ======================================================================
    FAIL: test_do_example_one_bad_patch (__main__.TestExampleOne)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/edwin/miniconda3/lib/python3.7/unittest/mock.py", line 1204, in patched
        return func(*args, **keywargs)
      File "<ipython-input-3-6c5d2713ecc1>", line 14, in test_do_example_one_bad_patch
        self.assertEqual(result, 8)
    AssertionError: 1434704449655547027 != 8
    
    ----------------------------------------------------------------------
    Ran 3 tests in 0.006s
    
    FAILED (failures=1)





    <unittest.main.TestProgram at 0x7f74b85e7240>



### Example 2


```python
from example_two import do_example_two


class TestExampleTwo(unittest.TestCase):
    def test_do_example_two_no_mock(self):
        result = do_example_two()
        self.assertTrue(isinstance(result, int))

    # This target is wrong because get_random_natural is not a member
    # of example_two scope
    @patch('example_two.get_random_natural', new=lambda: 8)
    def test_do_example_two_bad_patch(self):
        result = do_example_two()
        self.assertEqual(result, 8)

    # In this case example_two module loads the randomizers module,
    # so now it doesn't have an isolated instance of get_random_natural, it
    # has an instance of the whole randomizers module.
    # get_random_natural now can be looked up as an attribute of randomizers,
    # and that is our target.unittest
    # Bear in mind that in this particular case
    # 'example_two.randomizers.get_random_natural' equals 'randomizers.get_random_natural'
    # The former is explicit, "Explicit is better than implicit" Zen of Python
    @patch('example_two.randomizers.get_random_natural', new=lambda: 8)
    def test_do_example_two_good_patch(self):
        result = do_example_two()
        self.assertEqual(result, 8)

unittest.main(argv=['.', 'TestExampleTwo', '-v'], exit=False)

```

    test_do_example_two_bad_patch (__main__.TestExampleTwo) ... ERROR
    test_do_example_two_good_patch (__main__.TestExampleTwo) ... ok
    test_do_example_two_no_mock (__main__.TestExampleTwo) ... 

    
    I got 8
    
    I got 2438821792798670994


    ok
    
    ======================================================================
    ERROR: test_do_example_two_bad_patch (__main__.TestExampleTwo)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/home/edwin/miniconda3/lib/python3.7/unittest/mock.py", line 1196, in patched
        arg = patching.__enter__()
      File "/home/edwin/miniconda3/lib/python3.7/unittest/mock.py", line 1268, in __enter__
        original, local = self.get_original()
      File "/home/edwin/miniconda3/lib/python3.7/unittest/mock.py", line 1242, in get_original
        "%s does not have the attribute %r" % (target, name)
    AttributeError: <module 'example_two' from '/home/edwin/Notebooks/mocking/example_two.py'> does not have the attribute 'get_random_natural'
    
    ----------------------------------------------------------------------
    Ran 3 tests in 0.005s
    
    FAILED (errors=1)





    <unittest.main.TestProgram at 0x7f74b8570828>



## Ways of calling Patch

There are different ways of calling patch and some different patch flavors also. You will see how to patch by: decorating a function, decorating a class, using a context manager and manually starting and stoping a patch. Also I will list some guidelines on when to use each form





```python
from example_three import do_example_three, do_example_three_again

# We can apply patch at class level, this patch will affect all test methods
# and will be active throughout the life of the test case
@patch('example_three.print', new=lambda x: print(f'\n------ patched ------{x}'))
class TestPatchingShowcase(unittest.TestCase):

    # This is not new, we can apply a patch to a method
    # the mock will be active during the life of the function
    @patch('example_three.get_random_ratio')
    def test_patch_with_decorator(self, mocked_get_random_ratio):
        mocked_get_random_ratio.return_value = 0.5
        result = do_example_three()
        self.assertTrue(isinstance(mocked_get_random_ratio, unittest.mock.MagicMock))
        self.assertEqual(result, 0.5)

        # We can do some analysis of how the mock was used
        # https://docs.python.org/3.7/library/unittest.mock.html#unittest.mock.Mock.called
        self.assertTrue(mocked_get_random_ratio.called)

    def test_patch_with_context_manager(self):
        # This is how you can use a context manager for mocking,
        # the mock will be active during the life of the context manager scope.
        # Mocks created with context managers are the shortest lived ones
        with patch('example_three.get_random_ratio') as mocked_get_random_ratio:
            mocked_get_random_ratio.return_value = 0.21
            result = do_example_three()
        self.assertTrue(isinstance(mocked_get_random_ratio, unittest.mock.MagicMock))
        self.assertEqual(result, 0.21)

        # Here I invoque do_example_three not being mocked,
        # the following assert might not pass
        self.assertNotEqual(do_example_three(), 0.21)
    
    # This is perfectly valid mocking, but what happens if decorators starts to pile up?,
    # code starts to get messi, params list gets bigger and unreadable.
    # check next examples to see how to do this differently
    @patch('example_three.get_random_natural')
    @patch('example_three.get_random_ratio')
    def test_patch_many(self, get_random_ratio, get_random_natural):
        get_random_natural.return_value = 10
        get_random_ratio.return_value = .5
        result = do_example_three_again()
        self.assertEqual(result, 5)

unittest.main(argv=['.', 'TestPatchingShowcase', '-v'], exit=False)
```

    test_patch_many (__main__.TestPatchingShowcase) ... ok
    test_patch_with_context_manager (__main__.TestPatchingShowcase) ... ok
    test_patch_with_decorator (__main__.TestPatchingShowcase) ... 

    
    ------ patched ------
    I got 5.0
    
    ------ patched ------
    I got 0.21
    
    ------ patched ------
    I got 0.5499657579612143
    
    ------ patched ------
    I got 0.5


    ok
    
    ----------------------------------------------------------------------
    Ran 3 tests in 0.011s
    
    OK





    <unittest.main.TestProgram at 0x7f74b854e828>




```python
class TestMorePatchingShowcase(unittest.TestCase):
    
    # Readability is not the only reason one would want to
    # do this, that will depend on the use case
    def setUp(self):
        self.get_random_natural = patch('example_three.get_random_ratio').start()
        self.get_random_ratio = patch('example_three.get_random_natural').start()
        
        # tearDown is not the place to stop all mocks, because if an exception happens
        # during the test tearDown won't be executed. addCleanup is a better
        # place because the callback will be invoked no matter what, think of
        # this as a 'finally' clause for test cases
        self.addCleanup(patch.stopall)

    def test_manual_patching(self):
        self.get_random_natural.return_value = 10
        self.get_random_ratio.return_value = .5
        result = do_example_three_again()
        self.assertEqual(result, 5)

unittest.main(argv=['.', 'TestMorePatchingShowcase', '-v'], exit=False)
```

    test_manual_patching (__main__.TestMorePatchingShowcase) ... 

    
    I got 5.0


    ok
    
    ----------------------------------------------------------------------
    Ran 1 test in 0.004s
    
    OK





    <unittest.main.TestProgram at 0x7f74b8570198>



### When to use the different forms

This are some ideas to help you decide over one or another way of patching:

* _Decorator (functions and class)_: Good for quickly patching one depencency, which is **most of the time**.
* _Context Managers_: great when mocking standard library stuff or sensible dependencies. Don't use this to create multiple assertions in one test, create test functions for each case
* _Manual start and stop_: good for high customization and extremely long lived mocks

## Resources

* mock object library - patch  (https://docs.python.org/3.7/library/unittest.mock.html#unittest.mock.patch)
* Lisa Roach - Demystifying the Patch Function - PyCon 2018 (https://www.youtube.com/watch?v=ww1UsGZV8fQ)
* Scope of Variables in Python Tutorial (https://www.datacamp.com/community/tutorials/scope-of-variables-python)

