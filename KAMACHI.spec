# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

datas = [
    ('assets', 'assets'),
    ('storage', 'storage'),
    ('plugins', 'plugins'),
]

for extra_file in ['notes.txt', 'config.json', 'COMMANDS_LIST.txt', 'VERSION']:
    if os.path.exists(extra_file):
        datas.append((extra_file, '.'))

extra_binaries = []
try:
    datas += collect_data_files('llama_cpp')
    extra_binaries += collect_dynamic_libs('llama_cpp')
except Exception as e:
    pass

try:
    import llama_cpp
    llama_dir = os.path.dirname(llama_cpp.__file__)
    llama_lib_dir = os.path.join(llama_dir, 'lib')
    if os.path.exists(llama_lib_dir):
        datas.append((llama_lib_dir, 'llama_cpp/lib'))
except Exception as e:
    pass

hiddenimports = [
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'speech_recognition',
    'pyaudio',
    'pywhatkit',
    'geopy',
    'deep_translator',
    'requests',
    'bs4',
    'googlesearch',
    'screen_brightness_control',
    'psutil',
    'pyautogui',
    'PIL',
    'PIL.ImageGrab',
    'plyer',
    'plyer.platforms.win.notification',
    'pywinauto',
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'win32com.client',
    'pythoncom',
    'win32gui',
    'win32con',
    'win32process',
    # --- Kamachi 2.0 Core & Modular Subsystems ---
    'core',
    'core.intent',
    'core.context_manager',
    'core.intent_registry',
    'core.nlu_engine',
    'core.command_dispatcher',
    'core.event_bus',
    'core.plugin_loader',
    'core.safety',
    'voice',
    'voice.tts_engine',
    'voice.stt_engine',
    'voice.voice_customizer',
    'voice.multi_language',
    'voice.wake_word',
    'voice.noise_filter',
    'communication',
    'communication.contact_book',
    'communication.whatsapp_controller',
    'communication.email_controller',
    'automation',
    'automation.scheduler',
    'automation.proactive_agent',
    'memory',
    'memory.memory_store',
    'memory.user_preferences',
    'ai',
    'ai.gemini_client',
    'ai.code_generator',
    'ai.website_builder',
    'ai.autonomous_agent',
    'ai.emotional_ai',
    'ai.local_llm',
    'ai.gguf_runner',
    'ai.rag_engine',
    'voice.sister_tts',
    'vision',
    'vision.screen_agent',
    'ui',
    'ui.avatar_widget',
    'ui.notification_toast',
    'ui.dashboard_widget',
    'ui.sound_effects',
    'system_Control.app_adapters',
    'system_Control.app_adapters.office_adapter',
    # --- Legacy Subsystems ---
    'Education',
    'Education.coding_assist',
    'Education.social',
    'Education.table',
    'Education.math_operations',
    'system_Control',
    'system_Control.app',
    'system_Control.system_setting',
    'system_Control.voice_typing',
    'system_Control.screenshot_control',
    'system_Control.wifis',
    'system_Control.wifis.wifi_manager',
    'system_Control.wifis.voice_wifi',
    'system_Control.battry',
    'system_Control.battry.battery_manager',
    'system_Control.date_time',
    'system_Control.date_time.time_date_manager',
    'system_Control.date_time.voice_date_time',
    'system_Control.alarm',
    'system_Control.alarm.voice_alarm',
    'system_Control.alarm.alarm_manager',
    'system_Control.nearby',
    'system_Control.nearby.voice_nearby',
    'system_Control.hands_free_control',
    'news',
    'news.voice_news',
    'news.sports_news',
    'news.sports_news.voice_sports',
    'news.precious_metal',
    'news.precious_metal.voice_precious_metal',
    'call',
    'assistant_conversations',
    'file_management',
    'productivity',
    'smart_ai_chat',
    'web',
    'advanced_features',
    'config',
    'avatar_ui',
    'utils',
    'kamachi2_0',
]

a = Analysis(
    ['run_with_avatar.py'],
    pathex=['.'],
    binaries=extra_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tensorflow',
        'torch',
        'scipy',
        'cv2',
        'pandas',
        'IPython',
        'notebook',
        'pytest',
        'numpy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KAMACHI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/robot_avatar.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='KAMACHI',
)
