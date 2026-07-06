import os
import glob

def refactor():
    base_dir = "/home/ubuntu/scaler-education-journey/app/src"
    files = glob.glob(f"{base_dir}/**/*.jsx", recursive=True)
    
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
            
        if "fetch(" in content:
            # Replace absolute paths that start with '/api/'
            content = content.replace("fetch('/api/", "fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/")
            # Replace template literals that start with `/api/`
            content = content.replace("fetch(`/api/", "fetch(`${import.meta.env.VITE_API_BASE_URL || ''}/api/")
            
            with open(file, 'w') as f:
                f.write(content)
            print(f"Updated {file}")

if __name__ == "__main__":
    refactor()
