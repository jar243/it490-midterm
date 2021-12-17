import subprocess

def Start():
    p = subprocess.run(['service', 'it490-backend','start'], capture_output=True)
    print(p.stdout.decode('utf-8'))

def Status():
    p = subprocess.run(['service', 'it490-backend','status'], capture_output=True)
    print(p.stdout.decode('utf-8'))

def Stop():
    p = subprocess.run(['service', 'it490-backend','stop'], capture_output=True)
    print(p.stdout.decode('utf-8'))

