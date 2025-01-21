from pathlib import Path
import yaml
import re

def read_yaml(path):
    '''
        Function to read yaml file
    '''
    try:

        # Check if file name starts with '.github/workflows'
        if not re.search(r'^\.github/workflows/', path):
            raise PermissionError("Invalid workflow filepath")
        
        # Setting up trusted path/directory
        BASE_DIR = Path(".github/workflows").resolve()
        # Fetching user input absolute path
        abs_user_path = Path(path).resolve()


        # Comparing user input path against the trusted path
        if abs_user_path.parent != BASE_DIR:
            raise PermissionError("Invalid file path")

        # Get filename 
        user_path = re.split(r"^\.github/workflows/", path)[1]
        filename = Path(user_path)

        # Merging user path and trusted path 
        full_path = (BASE_DIR / filename).resolve()

        # Check if trusted path is within the resolved full path
        if not full_path.is_relative_to(BASE_DIR) and full_path.parent != BASE_DIR:
            raise PermissionError("Invalid file path")

        # Check if file extension is '.yaml' or '.yml' 
        if full_path.suffix not in ['.yaml', '.yml']:
            raise PermissionError("Not A YAML File")

        # Check if file exists
        if not full_path.is_file():
            raise FileNotFoundError("File does not exist.")


        with open(str(full_path), 'r') as file:
            yaml_content = yaml.safe_load(file)
            return yaml_content
            
    except Exception as e:
        print(f"Exception Occurred in read_yaml: {e}")
        return False