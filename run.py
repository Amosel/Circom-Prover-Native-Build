from jinja2 import Environment, FileSystemLoader
import os
import re
import subprocess
import argparse


def get_circom_files(directory):
    circom_files = []
    # List all files in the specified directory
    for file in os.listdir(directory):
        # Check if the file ends with '.circom'
        if file.endswith(".circom"):
            circom_files.append(file)
    return circom_files

def ask_user_to_choose_file(circom_files):
    print("Available .circom files:")
    for index, file in enumerate(circom_files):
        print(f"{index+1}. {file}")
    while True:
        choice = input("Choose a file number (or 'q' to quit): ")
        if choice.lower() == 'q':
            return None
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(circom_files):
                return circom_files[choice_index].split('.')[0]
            else:
                print("Invalid choice. Please enter a valid file number.")
        except ValueError:
            print("Invalid choice. Please enter a valid file number.")


def validate_includes(circom_file_path):
    # Regular expression to find include statements
    include_pattern = re.compile(r'include\s+"([^"]+)"')

    if not os.path.exists(circom_file_path):
        return f"File {circom_file_path} does not exist."

    with open(circom_file_path, 'r') as file:
        content = file.read()
    
    # Find all include statements
    includes = include_pattern.findall(content)

    missing_files = []
    for inc in includes:
        # Construct the full path for the included file
        inc_path = os.path.join(os.path.dirname(circom_file_path), inc)
        if not os.path.exists(inc_path):
            missing_files.append(inc_path)
    
    if missing_files:
        return "Missing include files: " + ", ".join(missing_files)
    else:
        return "All included files are present."

def clean(target, name):
    os.system(f"rm -rf ./src/{name}.cpp")
    os.system(f"rm -rf ./src/{name}.dat")

    while True:
        choice = input("Clean build folders? Y/n (anything else to skip): ")
        if choice.lower() == 'y':
            for cmd in [f"rm -rf ./build_{target}"]:
                print(cmd)
                os.system(cmd)
            return None
        else:
            return None


def identify_import_section_end(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    end_index = len(lines)
    for i, line in enumerate(lines):
        if not line.startswith('#include'):
            end_index = i
            break

    return end_index


"""
    This function adds a namespace to the generated cpp circuit file. 
"""


def add_namespace_to_cpp_circuit_file(name, build_dir):
    with open(f"./{build_dir}/{name}_cpp/{name}.cpp", 'r') as file:
        lines = file.readlines()

    end_index = len(lines)
    for i, line in enumerate(lines):
        if not line.startswith('#include'):
            end_index = i
            break

    patched_content = []
    patched_content.extend(lines[:end_index])
    patched_content.append(f'namespace {name} {{\n')
    patched_content.extend(lines[end_index + 1:])
    patched_content.append('} // namespace\n')

    with open(f"./src/{name}.cpp", 'w') as file:
        file.writelines(patched_content)


"""
    This function compiles a single circom circuit.
"""


def compile_one(name, build_dir, proof_directory):
    os.system(f"mkdir -p {build_dir}")
    print(f"Building {name}...")
    os.system(f"circom ./{proof_directory}/{name}.circom --c -o ./{build_dir}")
    print(f"Patching {name}...")
    add_namespace_to_cpp_circuit_file(name, build_dir)
    print(f"Copying Data {name}...")
    os.system(f"mv ./{build_dir}/{name}_cpp/{name}.dat ./src")
    print(f"Cleaning...")
    os.system(f"rm -rf ./{build_dir}")

def replace_tokens(string, tokens):
    for token in tokens:
        string = string.replace(token, '')
    return string


"""
    This function cleans generated files from 
"""


def clean_from_tempalte(template_dir, names):
    for dirpath, _, filenames in os.walk(template_dir):
        # Determine the relative path within the template directory
        output_subdir = os.path.relpath(dirpath, template_dir)
        # Create the corresponding output directory
        os.makedirs(output_subdir, exist_ok=True)

        for filename in filenames:
            if not filename.endswith(".j2"):
                continue
            # Determine the output file path for each name
            if '{{$1}}' in filename:
                for name in names:
                    filename = replace_tokens(filename, ['.j2', 'template.'])
                    output_file = os.path.join(
                        output_subdir, filename.replace('{{$1}}', name))
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(
                            f"The file '{output_file}' has been successfully removed.")
                    else:
                        print(f"The file '{output_file}' does not exist.")
            else:
                output_filename = replace_tokens(
                    filename, ['.j2', 'template.'])
                output_file = os.path.join(output_subdir, output_filename)
                if os.path.exists(output_file):
                    os.remove(output_file)
                    print(
                        f"The file '{output_file}' has been successfully removed.")
                else:
                    print(f"The file '{output_file}' does not exist.")


"""
    This function generates files from a template directory.
    The tempalte directory structure follow the following rulse:
        - Each file in the template directory is expected to be a jinja2 template, starting with 'template' and ending with '.j2'
        - Files containing '{{$1}}' will enumeate an by each items in the 'names' argument
        - Subdirectories wi
"""


def generate_from_tempalte(template_dir, names):
    env = Environment(loader=FileSystemLoader(template_dir))

    for dirpath, _, filenames in os.walk(template_dir):
        # Determine the relative path within the template directory
        output_subdir = os.path.relpath(dirpath, template_dir)
        # Create the corresponding output directory
        os.makedirs(output_subdir, exist_ok=True)

        for filename in filenames:
            if not filename.endswith(".j2"):
                continue
            # Determine the template file path
            template_file = os.path.join(output_subdir, filename)

            # Determine the output file path for each name
            if '{{$1}}' in filename:
                for name in names:
                    filename = replace_tokens(filename, ['.j2', 'template.'])
                    output_file = os.path.join(
                        output_subdir, filename.replace('{{$1}}', name))

                    print(
                        f"Rendering {template_file} for {name} at {output_file}")
                    # Render the template and write the output file
                    template = env.get_template(template_file)
                    output_content = template.render(namespace=name)

                    with open(output_file, 'w') as file:
                        file.write(output_content)

            else:
                output_filename = replace_tokens(
                    filename, ['.j2', 'template.'])
                output_file = os.path.join(output_subdir, output_filename)
                print(f"Rendering {template_file} at {output_file}")
                # Render the template and write the output file
                template = env.get_template(template_file)
                output_content = template.render(names=names)

                with open(output_file, 'w') as file:
                    file.write(output_content)

def build_targets(target, dirty):
    if dirty == False:
        subprocess.run(['make', 'clean'], check=True)
    try:
        # Run './build_gmp.sh target'
        subprocess.run(['sh', './build_gmp.sh', target], check=True)

        # Run 'make target'
        subprocess.run(['make', target], check=True)

        # Run 'xcodebuild' with specified arguments
        if target == 'ios':
            subprocess.run(['xcodebuild', '-target', 'install', '-configuration', 'Release', '-project', 'build_ios/circom.xcodeproj'], check=True)

        return "Build successful."

    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}"

parser = argparse.ArgumentParser(description='Compile Circom circuits.')
parser.add_argument('target', choices=["ios", "ios-simulator", "android_x86_64", "android", "host"], help='Path to the Circom proof directory')
parser.add_argument('proof_directory', type=str, help='Path to the Circom proof directory')
parser.add_argument('--dirty', action='store_true', help='Do not clean files from previous builds')
args = parser.parse_args()
proof_directory = args.proof_directory
dirty = args.dirty

def compile_circuits():
    # Using the 'proof_directory' variable from the parsed arguments
    build_dir = "build-cpp"
    circom_files = get_circom_files(proof_directory)
    if len(circom_files) == 0:
        print(f"No .circom files found in {proof_directory}")
        exit(0)

    circuit_name = ask_user_to_choose_file(circom_files)
    
    validate_includes(f"./{proof_directory}/{circuit_name}.circom")
    compile_one(circuit_name, build_dir, proof_directory)
    
    clean_from_tempalte('./template', list(map(lambda x: x.split('.')[0], circom_files)))
    generate_from_tempalte('./template', [circuit_name])
    
    build_targets('ios', dirty=dirty)
    
    clean_from_tempalte('./template', [circuit_name])
    clean('ios', circuit_name)
    exit(0)


compile_circuits()
