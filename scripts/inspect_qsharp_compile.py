import inspect
import qsharp

print('qsharp module file:', getattr(qsharp, '__file__', None))
print('has compile:', hasattr(qsharp, 'compile'))

compile_fn = qsharp.compile
print('compile signature:', inspect.signature(compile_fn))
print('\n--- doc ---\n')
print(compile_fn.__doc__)

# show source head
import inspect as _ins
try:
    src = _ins.getsource(compile_fn)
    print('\n--- source head ---\n', src.splitlines()[:30])
except Exception as e:
    print('Could not get source for compile:', e)
