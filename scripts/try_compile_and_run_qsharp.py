import qsharp
import time

QS_PATH = 'BS_GodFile/Content/Python/quantum/qsharp_layout_ranker.qs'
print('init')
qsharp.init(target_profile=qsharp.TargetProfile.Base)
with open(QS_PATH, 'r', encoding='utf-8') as f:
    src = f.read()

# Append a call expression so compile can parse an entry expression
call_expr = '\nlet _ = QuantumGameplay.Experiment.PickBestCandidate(0.2, 0.3, 0.8, 0.7);\n'
combined = src + call_expr
print('compiling combined length', len(combined))
try:
    program = qsharp.compile(combined)
    print('compiled program ok; QIR len', len(str(program)))
except Exception as e:
    print('compile failed:', type(e).__name__, e)
    raise

# Try qsharp.run by specifying shots and operation name
try:
    print('running via qsharp.run...')
    res = qsharp.run('QuantumGameplay.Experiment.PickBestCandidate', 1, 0.2, 0.3, 0.8, 0.7)
    print('qsharp.run result:', res)
except Exception as e:
    print('qsharp.run failed:', type(e).__name__, e)

# Simulate direct use via Python import (reload layout_ranker)
try:
    import importlib
    import BS_GodFile.Content.Python.quantum.layout_ranker as lr
    importlib.reload(lr)
    print('layout_ranker _QSHARP_AVAILABLE:', getattr(lr, '_QSHARP_AVAILABLE', False))
except Exception as e:
    print('layout_ranker reload failed:', type(e).__name__, e)

print('done')
