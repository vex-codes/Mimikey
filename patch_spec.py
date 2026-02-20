import re

with open('Mimikey.spec', 'r') as f:
    content = f.read()

plist_injection = """
info_plist={
    'NSAppleEventsUsageDescription': 'Mimikey needs to script Apple Events to function correctly over other apps.',
    'NSAccessibilityUsageDescription': 'Mimikey requires Accessibility permissions to listen for global hotkeys (F9/F10) and simulate intelligent typing.',
    'NSPrincipalClass': 'NSApplication',
    'NSHighResolutionCapable': 'True'
},
"""

# Insert info_plist inside the app = BUNDLE(...) block
content = re.sub(r'(BUNDLE\(.*?)(\n\))', r'\1,\n' + plist_injection + r'\2', content, flags=re.DOTALL)

with open('Mimikey2.spec', 'w') as f:
    f.write(content)
print("Spec file successfully patched with Info.plist")
