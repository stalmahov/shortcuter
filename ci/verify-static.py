"""Small local proof of scan exit codes. Does not start the application or DB."""
import json
import pathlib
import shutil
import subprocess
import tempfile

root = pathlib.Path(__file__).resolve().parents[1]
results = []
for bad in (False, True):
    with tempfile.TemporaryDirectory(prefix='lab6-proof-') as folder:
        target = pathlib.Path(folder)
        shutil.copytree(root / 'ci', target / 'ci')
        shutil.copy(root / '.gitleaks.toml', target / '.gitleaks.toml')
        (target / 'app').mkdir()
        source = ('import subprocess\ndef run(command):\n'
                  '    return subprocess.Popen(command, shell=True)\n') if bad else (
                  'def add(a, b):\n    return a + b\n')
        (target / 'app/sample.py').write_text(source)
        if bad:
            (target / 'fixture.env').write_text('POSTGRES_PASSWORD=lab6-disposable-example\n')
        else:
            (target / '.env.example').write_text('JWT_SECRET=\nPOSTGRES_USER=shortcuter\nPOSTGRES_PASSWORD=\nPOSTGRES_DB=shortcuter\n')
        for tool in ('bandit', 'gitleaks'):
            process = subprocess.run(['bash', str(target / 'ci' / (tool + '.sh'))],
                                     capture_output=True, text=True)
            expected = 1 if bad else 0
            record = dict(case='negative' if bad else 'clean', tool=tool,
                          exit=process.returncode, expected=expected)
            results.append(record)
            if process.returncode != expected:
                raise RuntimeError(f'Unexpected scan result: {record}')
            output = root / 'reports/static'
            output.mkdir(parents=True, exist_ok=True)
            shutil.copy(target / 'reports/static' / (tool + '.json'),
                        output / f'proof-{tool}-{bad}.json')
(root / 'reports/static/proof.json').write_text(json.dumps(results, indent=2))
print(json.dumps(results, indent=2))
