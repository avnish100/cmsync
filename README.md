# cmsync

An Image Sync Script for Sanity CMS. Automatically sync local images to your Sanity CMS project.

## Features

- Monitors local folder for new/modified images
- Uploads images to Sanity and creates corresponding documents
- Configurable via YAML file

## Prerequisites

- Python 3.6+
- Sanity CMS account and project

## Quick Start

1. Install required packages:
   ```
   pip install requests pyyaml
   ```

2. Create `config.yaml` in the script directory:
   ```yaml
   cms_type: sanity
   image_folder: /path/to/your/image/folder
   state_file: last_check_state.json

   sanity:
     project_id: your_sanity_project_id
     dataset: production
     api_version: "2023-05-03"
     token: your_sanity_token
   ```

3. Create an empty `last_check_state.json` file in the script directory:
   ```
   echo {} > state.json
   ```

4. Run the script:
   ```
   python image_sync_script.py
   ```

## Automation

### Unix/Linux/macOS:
Use cron to run daily at midnight:
```
0 0 * * * /usr/bin/python3 /path/to/your/image_sync_script.py
```

### Windows:
Use Task Scheduler:
- Create a new task
- Set trigger: Daily
- Action: Start a program
  - Program/script: `python.exe`
  - Add arguments: `C:\path\to\your\image_sync_script.py`

## How It Works

1. Reads config from `config.yaml`
2. Scans image folder
3. Uploads new/modified images to Sanity
4. Creates Sanity documents for new images
5. Updates `last_check_state.json` to track changes

## Extending to Other CMS Providers

The script is designed for easy extension to other CMS providers. Future versions may include support for WordPress, Contentful, etc.

## Contributing

Contributions welcome! Open an issue or submit a pull request.

## License

MIT License - see LICENSE file for details.
