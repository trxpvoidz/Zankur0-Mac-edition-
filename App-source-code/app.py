# app.py – Zankur0 macOS App (Flask backend + PyWebView window)
import os
import sys
import json
import shutil
import tempfile
import zipfile
import threading
from pathlib import Path
from io import BytesIO
from hashlib import sha256
from base64 import b64encode
import random
import string
import requests
from PIL import Image
from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
from flask_cors import CORS
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from werkzeug.utils import secure_filename
import webview

# ------------------- PyInstaller Path Detection -------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ------------------- Application Support Folder -------------------
if getattr(sys, 'frozen', False):
    APP_SUPPORT = Path.home() / "Library" / "Application Support" / "Zankur0"
else:
    APP_SUPPORT = Path(__file__).parent.absolute()

SKIN_PACK_DIR = APP_SUPPORT / "skin_packs"
SKIN_PACK_DIR.mkdir(parents=True, exist_ok=True)
STATE_FILE = SKIN_PACK_DIR / ".state.json"

FIXED_KEY = 's5s5ejuDru4uchuF2drUFuthaspAbepE'

# Manifest options (include all as before)
MANIFEST_OPTIONS = {
    "1st Birthday": '{"header":{"version":[1,0,5],"description":"pack.description","name":"pack.name","uuid":"202539ce-e6c5-40b5-a4a1-4296277d18f6"},"modules":[{"version":[1,0,5],"type":"skin_pack","uuid":"ef6f8811-933b-4673-b285-c02cf583e56d"}],"format_version":1}',
    "1st Animal Friends": '{"format_version":1,"header":{"name":"1st Animal Friends","uuid":"9a9fa850-0b5e-11ee-9a0f-a795af90f04f","version":[1,0,3]},"modules":[{"type":"skin_pack","uuid":"a162eb70-0b5e-11ee-86cb-9d9dd4413780","version":[1,0,3]}]}',
    "Beap Borp HD": '{"header":{"name":"BeepBorpHD","version":[1,0,4],"uuid":"18215a23-e943-4004-b799-48fdcc926799"},"modules":[{"version":[1,0,4],"type":"skin_pack","uuid":"7eb2682d-9532-4db6-aa7e-b4512e347f2e"}],"format_version":1}',
    "Blockheads": '{"header": {"name": "Blockheads","version": [1,0,0],"uuid": "8b8362a3-cd8c-4f48-9a49-b494659513b6"},"modules": [{"version": [1,0,0],"type": "skin_pack","uuid": "c47ad348-0f17-438f-ae11-6c001445a947"}],"format_version": 1}',
    "Crafty Costumes": '{"format_version":1,"header":{"name":"CraftyCostumes","uuid":"c35ad990-3dc5-4179-bfe9-6f323d94f0b2","version":[1,0,11]},"modules":[{"type":"skin_pack","uuid":"a568d136-49ec-4287-bbe1-29110643a489","version":[1,0,11]}]}',
    "Creepy Creatures": '{"header": {"name": "Creepy Creatures","version": [1,0,1],"uuid": "dd44b7d6-2c05-48a2-bfdf-f78596b59f44"},"modules": [{"version": [1,0,1],"type": "skin_pack","uuid": "f84c0b4a-7b0b-4ed3-9125-dffa2815809f"}],"format_version": 1}',
    "Cute Kitty HD": '{"header":{"name":"CuteKittyHD","version":[1,0,10],"uuid":"7124cf9d-5d0e-4865-9656-03c1f04039c3"},"modules":[{"version":[1,0,10],"type":"skin_pack","uuid":"e9c920a2-fbb1-430a-a951-f240f48c5abc"}],"format_version":1}',
    "Cyborg Skin Pack": '{"header": {"description": "Cyborg Skin Pack","name": "Cyborg Skin Pack","version": [1,0,4],"uuid": "deb3b920-be8a-4b62-b8b1-5c9c7a4272f9"},"modules": [{"version": [1,0,4],"type": "skin_pack","uuid": "94d873ba-6fe7-4374-b5a4-cb36a285fd49"}],"format_version": 1}',
    "Dress Code": '{"header": {"name": "Dress Code","version": [1,0,6],"uuid": "f47107de-385d-4e15-8a5a-cdd40a1df33d"},"modules": [{"version": [1,0,6],"type": "skin_pack","uuid": "683735a6-44f6-40e2-97b0-5039f5251353"}],"format_version": 1}',
    "Builders & Biomes": '{"format_version":1,"header":{"name":"BuildersBiomes","uuid":"05ead86c-572c-40c8-8cb0-8733a7894185","version":[1,0,4]},"modules":[{"type":"skin_pack","uuid":"9d6e6755-42dc-4ac9-8cc8-374a4ca9a9ab","version":[1,0,4]}]}',
    "Haipu": '{"format_version":1,"header":{"name":"Haipu","uuid":"f46a707a-36c7-45d0-becf-88c5e2f4257d","version":[1,0,3]},"modules":[{"type":"skin_pack","uuid":"2791e9a8-e380-4e14-8f9c-6d3c3aa3476b","version":[1,0,3]}]}',
    "Heartfelt": '{"header": {"name": "Heartfelt","version": [1, 0, 0],"uuid": "72fe6a92-121d-40a7-bb47-d08a41579d32"},"modules": [{"version": [1, 0, 0],"type": "skin_pack","uuid": "31a2afa5-b024-444a-822b-46d4bd1dd2c6"}],"format_version": 1}',
    "Lunar New Year of The Ox": '{"header":{"name":"Lunar_New_Year_of_The_Ox","version":[1,0,12],"uuid":"96e8daad-3d7a-4818-bc25-2c815fb3bbc2"},"modules":[{"version":[1,0,12],"type":"skin_pack","uuid":"bed5e4b3-b108-4448-b608-0908e7905db5"}],"format_version":1}',
    "Minecraft x Uniqlo Skins Vol 2": '{"format_version":1,"header":{"name":"pack.name","uuid":"18219eb4-d96f-4b8b-999a-6cbd1b65c58d","version":[1,0,5]},"modules":[{"type":"skin_pack","uuid":"77260103-f950-4280-9a17-89da92391898","version":[1,0,5]}],"metadata":{"authors":["Mike Gaboury"]}}',
    "Norse Mythology Bonus Skins": '{"format_version":1,"header":{"name":"pack.name","uuid":"6dd86351-0191-4a3e-85cf-2a81647b830c","version":[1,0,5]},"modules":[{"type":"skin_pack","uuid":"a29a25d5-4b28-4ddb-a57d-ce272cf5fc39","version":[1,0,5]}]}',
    "Notice Me Senpai HD": '{"header":{"name":"NoticeMeHD","version":[1,0,2],"uuid":"4bf4b0f7-dec8-4cde-b6f4-0222972d0aac"},"modules":[{"version":[1,0,2],"type":"skin_pack","uuid":"39e6f01a-da8a-4106-b66f-a643fbaee1c9"}],"format_version":1}',
    "Onesie Skeletons": '{"header":{"name":"OnesieSkeletons","version":[1,0,3],"uuid":"87e7495b-a219-4a65-837c-654ee97ad8f6"},"modules":[{"version":[1,0,3],"type":"skin_pack","uuid":"d164c220-a005-466d-ac87-d096e08337d7"}],"format_version":1}',
    "Popya": '{"format_version":1,"header":{"name":"Popya","uuid":"e3f6e616-ca3c-492c-bbbf-4d41b859b8cd","version":[1,0,5]},"modules":[{"type":"skin_pack","uuid":"52e87833-4d00-47bb-abb1-62731227a037","version":[1,0,5]}]}',
    "Rockin' Holiday": '{"format_version":1,"header":{"name":"RockinHoliday","uuid":"0887d1fd-a752-47d9-a119-b47e6a5fac67","version":[1,0,7]},"modules":[{"type":"skin_pack","uuid":"d8c125af-9c41-4e0c-998f-52961a0c2a0d","version":[1,0,7]}]}',
    "Safari Adventurers": '{"header": {"name": "Safari Adventurers Skin Pack","version": [1,0,1],"uuid": "219655ca-39b4-4ec4-b04b-281a6ac1e3e5"},"modules": [{"version": [1,0,1],"type": "skin_pack","uuid": "3ad7c0f9-13a0-4e19-861a-04f336eec2a8"}],"format_version": 1}',
    "Sailor Uniform": '{"format_version":1,"header":{"name":"Sailor Uniform","uuid":"00e87c90-b734-4021-88b3-7cca436747cc","version":[1,0,10]},"modules":[{"type":"skin_pack","uuid":"73b4293b-c91b-4d9b-9f12-d00d9455d2b9","version":[1,0,10]}]}',
    "Stay Warm HD": '{"header":{"name":"StayWarmHD","version":[1,0,3],"uuid":"85a2ede9-cce0-42e4-96af-c9fd1e913b37"},"modules":[{"version":[1,0,3],"type":"skin_pack","uuid":"b0afc709-4c72-4578-953b-146f3270bcb7"}],"format_version":1}',
    "Summer Beach Party": '{"format_version": 1,"metadata": {"authors": ["GoE-Craft","All Rights Reserved."]},"header": {"name": "SummerBeachPartySkinPack","uuid": "6fef41b8-4000-4afc-ae5d-03b08755a8e4","version": [1,0,0]},"modules": [{"type": "skin_pack","uuid": "683da9cd-a504-4001-b0bf-400991218560","version": [1,0,0]}]}',
    "Summer Gift": '{"header":{"name":"pack.SummerGift","version":[1,0,1],"uuid":"aed5c500-83e9-44f6-9213-618a9dd32e3e"},"modules":[{"version":[1,0,1],"type":"skin_pack","uuid":"c9fe656a-9cad-48a9-97db-860e1f90021b"}],"format_version":1}',
    "Superman": '{"format_version":1,"header":{"name":"pack.name","version":[1,0,6],"uuid":"50a5f49f-86b3-3b7e-3060-d40000f59dcb"},"modules":[{"version":[1,0,6],"type":"skin_pack","uuid":"0e837629-6794-2d56-76ef-174bb282f3ca"}]}',
    "Timless Toys": '{"format_version":1,"header":{"name":"Timeless Toys Skins","uuid":"727df6bb-5392-4b92-b262-54545731116a","version":[1,0,3]},"modules":[{"type":"skin_pack","uuid":"cbc1286c-aa81-427a-9360-0a9c4042da0a","version":[1,0,3]}]}',
    "Vibrant Adventurers Volume 1": '{"header":{"name":"VibrantAdventurersV1","version":[1,0,1],"uuid":"5cfc95c0-7490-4bdd-a5f9-d1164decbb1b"},"modules":[{"version":[1,0,0],"type":"skin_pack","uuid":"d2dbc6e4-956e-4c7d-83b1-70437a168f3a"}],"format_version":1}',
    "Vibrant Adventurers Volume 2": '{"header":{"name":"VibrantAdventurersV2","version":[1,0,3],"uuid":"b3b5a06a-7dc6-4ec6-a3cc-89c46f9a91e2"},"modules":[{"version":[1,0,0],"type":"skin_pack","uuid":"7e4831cb-9912-4cd3-83a0-76ffee9104d5"}],"format_version":1}',
    "Vibrant Adventurers Volume 3": '{"header":{"name":"VibrantAdventurersV3","version":[1,0,1],"uuid":"ba692d28-b4ca-40ce-9e0e-7f7960baee13"},"modules":[{"version":[1,0,0],"type":"skin_pack","uuid":"96456913-21cc-4b12-99bb-a6f937c9bec1"}],"format_version":1}',
    "Wild West Adventurers": '{"header": {"name": "Cowboys and Indians","version": [1,0,4],"uuid": "222b52e7-d292-4765-838c-66d8cbb4719d"},"modules": [{"version": [1,0,4],"type": "skin_pack","uuid": "942e9425-18c8-4246-9a90-0af9804e3d40"}],"format_version": 1}',
    "Winter Whimsy": '{"header": {"name": "WinterWhimsy","version": [1, 0, 0],"uuid": "163b24c0-5989-4457-a68f-fbbb6099c842"},"modules": [{"version": [1, 0, 0],"type": "skin_pack","uuid": "3b8b7a48-b62a-44a7-b1ff-d93098c31cc6"}],"format_version": 1}',
    "Young Fashion": '{"header": {"name": "Young Fashion","version": [1,0,1],"uuid": "7fdde03a-8dce-4b76-a969-6484d79358fd"},"modules": [{"version": [1,0,1],"type": "skin_pack","uuid": "944a69ab-c924-4155-ad7b-a4f13742fb86"}],"format_version": 1}',
    "Young Gru": '{"header":{"name":"Young Gru","version":[1,0,8],"uuid":"670f5c25-c3a2-4a87-b48c-313b8ee35578"},"modules":[{"version":[1,0,8],"type":"skin_pack","uuid":"e84a3684-808a-42e5-8a68-610c3cb8adb8"}],"format_version":1}'
}

# ------------------- Encryption Functions (unchanged) -------------------
fileSkip = {'manifest.json', 'pack_icon.png'}
fileSkipForce = {'contents.json', 'signatures.json', 'contentsDecrypted.json', 'signaturesDecrypted.json'}
fileSkipFull = fileSkip | fileSkipForce

def generateKey(pathOrByte, isPath, isKeyRandom, variableOrFile):
    if isKeyRandom == True:
        key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    else:
        key = isKeyRandom

    cipher = Cipher(algorithms.AES(key.encode('utf-8')), modes.CFB8(key[:16].encode('utf-8')), backend=default_backend())
    encryptor = cipher.encryptor()

    if isPath == True:
        with open(pathOrByte, 'rb') as file:
            fileRead = file.read()
            write = encryptor.update(fileRead) + encryptor.finalize()
            with open(pathOrByte, 'wb') as file:
                file.write(write)
        return key, None
    elif variableOrFile == True:
        encryptedVariable = encryptor.update(pathOrByte) + encryptor.finalize()
        return key, encryptedVariable
    else:
        with open(variableOrFile, 'wb') as file:
            file.write(encryptor.update(pathOrByte) + encryptor.finalize())
        return key, None

def tool_encrypt_pack(inputPath, keyPack, debug=False):
    inputPathPack = os.path.join(os.path.abspath(inputPath), '')
    fileJSONContents = {"version": 1, "content": []}

    for path, dirs, files in os.walk(inputPathPack):
        for file in files:
            pathFile = os.path.join(path, file)
            if pathFile.startswith(os.path.join(inputPath, 'texts', '')):
                doEncrypt = False
                doNotAdd = False
            else:
                breakLoop = False
                for pathFileSkip in fileSkipFull:
                    if not breakLoop:
                        if pathFile.startswith(os.path.join(inputPath, pathFileSkip)):
                            doEncrypt = False
                            isForce = False
                            for pathFileSkipForce in fileSkipForce:
                                if pathFile.startswith(os.path.join(inputPath, pathFileSkipForce)):
                                    isForce = True
                                    break
                            doNotAdd = isForce
                            breakLoop = True
                            break
                        else:
                            doEncrypt = True
                    else:
                        break

            if doEncrypt:
                key, _ = generateKey(pathFile, True, True, True)
                fileJSONContents["content"].append({'key': key, 'path': pathFile.replace(inputPathPack, "").replace("\\", "/")})
            elif not doNotAdd:
                fileJSONContents["content"].append({'path': pathFile.replace(inputPathPack, "").replace("\\", "/")})

    with open(os.path.join(inputPathPack, 'contents.json'), 'wb') as fileContents:
        with open(os.path.join(inputPathPack, 'manifest.json'), 'r') as file:
            jsonManifest = json.load(file)
            jsonUUID = jsonManifest['header']['uuid']

        with open(os.path.join(inputPathPack, 'manifest.json'), 'rb') as fileManifest:
            hashVal = b64encode(sha256(fileManifest.read()).digest()).decode()
            fileJSONSignatures = [{"hash": hashVal, "path": "manifest.json"}]
            sig_path = os.path.join(inputPathPack, 'signatures.json')
            fileJSONSignatures_bytes = json.dumps(fileJSONSignatures, separators=(',', ':')).encode('utf-8')
            key_sig, _ = generateKey(fileJSONSignatures_bytes, False, True, sig_path)
            fileJSONContents["content"].append({'key': key_sig, 'path': 'signatures.json'})

        headerByte = b'\xfc\xb9\xcf\x9b\x00\x00\x00\x00\x00\x00\x00\x00\x24'
        empty = bytes(256)
        contents_bytes = json.dumps(fileJSONContents, separators=(',', ':')).encode('utf-8')
        key_contents, encryptedVariable = generateKey(contents_bytes, False, keyPack, True)
        headerFinal = empty[:4] + headerByte + jsonUUID.encode('utf-8') + empty[53:] + encryptedVariable
        fileContents.write(headerFinal)

        if debug:
            with open(os.path.join(inputPathPack, 'contentsDecrypted.json'), 'wb') as f:
                f.write(contents_bytes)
            with open(os.path.join(inputPathPack, 'signaturesDecrypted.json'), 'wb') as f:
                f.write(fileJSONSignatures_bytes)

    return jsonUUID

def setup_and_encrypt(inputPath, copy=False, customManifest=None, keyPack=FIXED_KEY, debug=False):
    inputPathPack = os.path.join(os.path.abspath(inputPath), '')
    manifest_path = os.path.join(inputPathPack, 'manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        jsonManifest = json.load(f)

    if jsonManifest['modules'][0]['type'] == 'world_template':
        raise ValueError("World Template packs are not supported.")

    uuid = jsonManifest['header']['uuid']
    if len(uuid) != 36:
        raise ValueError('Invalid UUID in manifest.json')

    if customManifest:
        if not customManifest.lower().endswith('.json'):
            raise ValueError('Custom manifest must be a JSON file.')
        shutil.copy(customManifest, manifest_path)

    if len(keyPack) != 32:
        raise ValueError('Key must be 32 bytes long.')

    if copy:
        shutil.copytree(inputPathPack, inputPath + "-COPY")

    uuid = tool_encrypt_pack(inputPath, keyPack, debug)
    return uuid

# ------------------- Utility Functions -------------------
def load_state():
    state = {"known": []}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except:
            pass
    return state

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def find_manifest(folder):
    for r, _, f in os.walk(folder):
        if "manifest.json" in f:
            return Path(r) / "manifest.json"
    return None

def read_manifest(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["header"]["uuid"], data["header"].get("version", [0,0,0])

def get_pack_display_name(pack_path: Path) -> str:
    texts_dir = pack_path / "texts"
    if texts_dir.exists():
        for lang_file in texts_dir.glob("*.lang"):
            try:
                with open(lang_file, 'r', encoding='utf-8-sig') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('skinpack.') and '=' in line:
                            return line.split('=', 1)[1].strip()
            except:
                continue
    return pack_path.name

def scan_local_packs():
    state = {"known": []}
    for folder in SKIN_PACK_DIR.iterdir():
        if not folder.is_dir():
            continue
        manifest = find_manifest(folder)
        if not manifest:
            continue
        try:
            uuid, version = read_manifest(manifest)
        except:
            continue
        display_name = get_pack_display_name(folder)
        state["known"].append({
            "uuid": uuid,
            "version": version,
            "path": str(folder),
            "store_name": display_name,
            "source": "local"
        })
    save_state(state)
    return state

def find_pack_root_porter(folder: Path) -> Path:
    for root, dirs, files in os.walk(folder):
        if "manifest.json" in files:
            return Path(root)
    if (folder / "manifest.json").exists():
        return folder
    raise ValueError("manifest.json not found anywhere in the uploaded folder")

def copy_pack_first(folder):
    actual_root = find_pack_root_porter(Path(folder))
    print(f"Found pack root: {actual_root}")

    temp_root = os.path.join(tempfile.gettempdir(), "porter_temp")
    if os.path.exists(temp_root):
        shutil.rmtree(temp_root, ignore_errors=True)
    os.makedirs(temp_root, exist_ok=True)
    temp_dest = os.path.join(temp_root, "pack_to_encrypt")
    os.makedirs(temp_dest, exist_ok=True)

    for item in os.listdir(actual_root):
        src = os.path.join(actual_root, item)
        dst = os.path.join(temp_dest, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"Copied pack contents to: {temp_dest}")
    return temp_dest

# ------------------- Flask App -------------------
if getattr(sys, 'frozen', False):
    template_folder = resource_path('templates')
    static_folder = resource_path('assets')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
    app = Flask(__name__)

CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    if getattr(sys, 'frozen', False):
        return send_from_directory(app.static_folder, filename)
    else:
        return send_from_directory('assets', filename)

@app.route('/api/open-folder')
def open_folder():
    import subprocess
    subprocess.Popen(['open', str(SKIN_PACK_DIR)])
    return jsonify({"status": "opened"})

@app.route('/api/state')
def get_state():
    return jsonify(load_state())

@app.route('/api/scan', methods=['POST'])
def scan():
    return jsonify(scan_local_packs())

@app.route('/api/upload-zip', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    if not file.filename.lower().endswith('.zip'):
        return jsonify({"error": "Only ZIP files allowed"}), 400

    try:
        tmp_dir = Path(tempfile.gettempdir()) / "Zankur0_uploads"
        tmp_dir.mkdir(exist_ok=True)
        zip_path = tmp_dir / secure_filename(file.filename)
        file.save(zip_path)
        return jsonify({"status": "uploaded", "temp_path": str(zip_path)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload-folder', methods=['POST'])
def upload_folder():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400

    files = request.files.getlist('files[]')
    if not files:
        return jsonify({"error": "No files"}), 400

    try:
        tmp_root = Path(tempfile.gettempdir()) / "Zankur0_uploads" / f"folder_{os.urandom(4).hex()}"
        tmp_root.mkdir(parents=True, exist_ok=True)

        for file in files:
            rel_path = file.filename.replace('\\', '/')
            if rel_path.startswith('/'):
                rel_path = rel_path[1:]
            if '..' in rel_path:
                continue
            dest_path = tmp_root / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(dest_path)

        return jsonify({"status": "uploaded", "temp_path": str(tmp_root)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/install', methods=['POST'])
def install_pack():
    data = request.json
    source_path = Path(data['source_path'])
    is_zip = data.get('is_zip', True)
    pack_name = data.get('name', source_path.stem)
    encrypt = data.get('encrypt', False)
    manifest_choice = data.get('manifest_choice', None)

    try:
        if is_zip:
            temp_extract = SKIN_PACK_DIR / "__temp_install__"
            if temp_extract.exists():
                shutil.rmtree(temp_extract)
            temp_extract.mkdir()
            with zipfile.ZipFile(source_path, 'r') as z:
                z.extractall(temp_extract)
            pack_root_candidate = temp_extract
        else:
            pack_root_candidate = source_path

        manifest_path = find_manifest(pack_root_candidate)
        if not manifest_path:
            raise Exception("manifest.json not found")

        if encrypt and manifest_choice:
            temp_copy = copy_pack_first(str(pack_root_candidate))
            manifest_path_copy = find_manifest(temp_copy)
            with open(manifest_path_copy, 'w', encoding='utf-8') as f:
                f.write(MANIFEST_OPTIONS[manifest_choice])
            setup_and_encrypt(temp_copy, copy=False, customManifest=None, keyPack=FIXED_KEY)
            pack_root_candidate = Path(temp_copy)
            manifest_path = find_manifest(pack_root_candidate)

        uuid, version = read_manifest(manifest_path)

        state = load_state()
        existing = next((p for p in state['known'] if p['uuid'] == uuid), None)
        if existing:
            shutil.rmtree(existing['path'], ignore_errors=True)
            state['known'] = [p for p in state['known'] if p['uuid'] != uuid]

        dest_folder = SKIN_PACK_DIR / pack_name
        if dest_folder.exists():
            shutil.rmtree(dest_folder, ignore_errors=True)

        pack_root = manifest_path.parent
        shutil.copytree(pack_root, dest_folder)

        if is_zip:
            shutil.rmtree(pack_root_candidate, ignore_errors=True)

        display_name = get_pack_display_name(dest_folder)
        state['known'].append({
            "uuid": uuid,
            "version": version,
            "path": str(dest_folder),
            "store_name": display_name,
            "source": "store" if is_zip else "local"
        })
        save_state(state)

        return jsonify({"status": "installed", "uuid": uuid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/delete', methods=['POST'])
def delete_pack():
    data = request.json
    uuid = data['uuid']
    state = load_state()
    pack = next((p for p in state['known'] if p['uuid'] == uuid), None)
    if pack:
        shutil.rmtree(pack['path'], ignore_errors=True)
        state['known'] = [p for p in state['known'] if p['uuid'] != uuid]
        save_state(state)
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Pack not found"}), 404

@app.route('/api/wipe', methods=['POST'])
def safe_wipe():
    state = load_state()
    for pack in state['known']:
        shutil.rmtree(pack['path'], ignore_errors=True)
    state['known'] = []
    save_state(state)
    return jsonify({"status": "wiped"})

@app.route('/api/porter', methods=['POST'])
def run_porter():
    data = request.json
    folder_path = data['folder']
    manifest_choice = data['manifest_choice']
    try:
        temp_copy = copy_pack_first(folder_path)
        manifest_path = find_manifest(temp_copy)
        if not manifest_path:
            raise Exception("manifest.json not found after copy")

        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(MANIFEST_OPTIONS[manifest_choice])
        uuid = setup_and_encrypt(temp_copy, copy=False, customManifest=None, keyPack=FIXED_KEY)

        # Create ZIP in Downloads
        downloads_folder = Path.home() / 'Downloads'
        zip_filename = f"{Path(folder_path).name}_encrypted.zip"
        output_path = downloads_folder / zip_filename

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(temp_copy):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_copy)
                    zf.write(file_path, arcname)

        shutil.rmtree(temp_copy, ignore_errors=True)

        # Also send as downloadable response (frontend will trigger download)
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(temp_copy):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_copy)
                    zf.write(file_path, arcname)
        zip_buffer.seek(0)

        response = send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        response.headers['X-Pack-UUID'] = uuid
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/manifest-options')
def manifest_options():
    return jsonify(list(MANIFEST_OPTIONS.keys()))

@app.route('/api/thumbnail/local')
def local_thumbnail():
    path = request.args.get('path', '')
    if not path or not os.path.exists(path):
        return '', 404
    try:
        img = Image.open(path)
        img.thumbnail((200, 200))
        buf = BytesIO()
        img.save(buf, "PNG")
        buf.seek(0)
        return send_file(buf, mimetype='image/png')
    except:
        return '', 404

# ------------------- Start Flask in Thread -------------------
def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    window = webview.create_window(
        title='Zankur0',
        url='http://127.0.0.1:5000',
        width=1000,
        height=750,
        resizable=True,
        min_size=(800, 600)
    )
    webview.start()