import os
import shutil
import subprocess

# Define a list of files to ignore
IGNORE_FILES = ['main.py']

def create_build_directory_structure(src, dest):
    """
    Create the directory structure in the destination path mirroring the source path, skipping hidden folders.
    """
    if not os.path.exists(dest):
        os.makedirs(dest)
    # Else, wipe everything in the directory
    else:
        shutil.rmtree(dest)
        os.makedirs(dest)

    for root, dirs, files in os.walk(src):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for dir_ in dirs:
            dest_dir = os.path.join(dest, os.path.relpath(os.path.join(root, dir_), src))
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

def copy_non_python_files(src, dest):
    """
    Copy all non-python files from the source to the destination directory, skipping hidden folders.
    """
    for root, dirs, files in os.walk(src):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.py') and not file.startswith('.'):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest, os.path.relpath(src_file, src))
                shutil.copy2(src_file, dest_file)
                print(f"Copied {src_file} to {dest_file}")
            elif file in IGNORE_FILES:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest, os.path.relpath(src_file, src))
                shutil.copy2(src_file, dest_file)
                print(f"Copied {src_file} to {dest_file}")

def compile_python_files(src, dest, mpy_cross_path):
    """
    Compile Python files to .mpy files and save them in the destination directory, skipping hidden folders and ignored files.
    """
    for root, dirs, files in os.walk(src):
        # Skip hidden folders
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.') and file not in IGNORE_FILES:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest, os.path.relpath(src_file, src)).replace('.py', '.mpy')
                compile_to_mpy(src_file, dest_file, mpy_cross_path)

def compile_to_mpy(src_file, dest_file, mpy_cross_path):
    """
    Use mpy-cross to compile a Python file to an .mpy file.
    """
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)

        # Compile the .py file to .mpy
        subprocess.run([mpy_cross_path,'-O3', src_file, '-o', dest_file], check=True)
        print(f"Compiled {src_file} to {dest_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error compiling {src_file}: {e}")

def main():
    src_dir = '/Users/sebastiaan.provost/Workspace/BHV/Badges/BHV_Badge_2024/firmware'
    build_dir = '/Users/sebastiaan.provost/Workspace/BHV/Badges/BHV_Badge_2024/build'
    #mpy_cross_path = '/Users/sebastiaan.provost/Workspace/BHV/Badges/BHV_Badge_2024/tools/mpy-cross'
    mpy_cross_path = 'mpy-cross'

    # Create the directory structure in the build directory
    create_build_directory_structure(src_dir, build_dir)

    # Copy all non-python files to the build directory
    copy_non_python_files(src_dir, build_dir)

    # Compile all python files to .mpy and save them in the build directory
    compile_python_files(src_dir, build_dir, mpy_cross_path)

if __name__ == '__main__':
    main()
