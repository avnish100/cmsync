import os
import hashlib
import json
import requests
import yaml
from pathlib import Path
from abc import ABC, abstractmethod

with open("config.yaml","r") as config_file:
    config = yaml.safe_load(config_file)

IMAGE_FOLDER = config['image_folder']
STATE_FILE = config['state_file']

class CMSProvider(ABC):
    @abstractmethod 
    def upload_image(self,image_path):
        pass
    
    @abstractmethod
    def create_document(self,title,image_id):
        pass

class SanityProvider(CMSProvider):
    def __init__(self,config):
        self.project_id = config['project_id']
        self.dataset = config['dataset']
        self.api_version = config['api_version']
        self.token = config['token']
        self.type = config['type']

    def upload_image(self, image_path):
        with open(image_path, "rb") as f:
            response = requests.post(
                f"https://{self.project_id}.api.sanity.io/v{self.api_version}/assets/images/{self.dataset}",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "image/jpeg"
                },
                data=f
            )
        response.raise_for_status()
        return response.json()["document"]["_id"]
    
    def create_document(self, title, image_id):
        document = {
            "_type": self.type,
            "title": title,
            "image": {
                "_type": "image",
                "asset": {
                    "_type": "reference",
                    "_ref": image_id
                }
            }
        }
        response = requests.post(
            f"https://{self.project_id}.api.sanity.io/v{self.api_version}/data/mutate/{self.dataset}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            },
            json={
                "mutations": [
                    {
                        "create": document
                    }
                ]
            }
        )
        response.raise_for_status()
        return response.json()

def get_cms_provider():
    cms_type = config['cms_type']
    if cms_type == 'sanity':
        return SanityProvider(config['sanity'])
    else:
        raise ValueError(f"Unsupported CMS type: {cms_type}")

def get_image_hash(file_path):
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def load_last_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}

def save_current_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    cms_provider = get_cms_provider()
    last_state = load_last_state()
    current_state = {}

    for file_name in os.listdir(IMAGE_FOLDER):
        if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            file_path = os.path.join(IMAGE_FOLDER, file_name)
            file_hash = get_image_hash(file_path)
            current_state[file_name] = file_hash

            if file_name not in last_state or last_state[file_name] != file_hash:
                print(f"New or updated image found: {file_name}")
                
                title = Path(file_name).stem.replace('_', ' ')
                
                image_id = cms_provider.upload_image(file_path)
                cms_provider.create_document(title, image_id)
                
                print(f"Created new document for {file_name}")

    save_current_state(current_state)
    print("Sync completed.")

if __name__ == "__main__":
    main()