# Circom Prover Native Build

| Currently supporting iOS. Should be not too hard to add android support.

1. Prepare Circom Circuit: Create your circuit in Circom 
2. Setup download and compile dependencies `python setup.py`
3. Compile Circuit, Compile targets `python run.py {target} {directory}` where `target` can be `ios`, `ios-simulator`, `android`, `android_x86_64`, and `host`.

Final results are in the `package_{target}` directory.

clean:
`make clean`