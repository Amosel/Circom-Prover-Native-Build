import subprocess

def build_targets():
    try:
        subprocess.run(['git' 'submodule' 'update' '--init' '--recursive'], check=True)

        subprocess.run(['sh', './patch.sh'], check=True)

        return "Success."

    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}"
