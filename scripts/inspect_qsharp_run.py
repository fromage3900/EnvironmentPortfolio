import inspect
import qsharp
print('qsharp.run signature:', inspect.signature(qsharp.run))
print('\nqsharp.run doc:\n')
print(qsharp.run.__doc__)
