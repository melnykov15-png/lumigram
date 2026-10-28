#!/usr/bin/env python3
"""Applies the Lumigram mod on top of a Swiftgram checkout.

Usage: python3 mod/apply_mod.py <path-to-swiftgram-checkout>

Every edit is an exact text replacement that must match exactly once, so when
upstream changes the anchor the build fails here with a clear message instead
of silently producing a broken app.
"""
import os
import shutil
import sys

MOD_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "Lumigram"

EDITS = [
    # --- Free Apple ID: no app extensions (each one would need its own App ID) ---
    (
        "Telegram/BUILD",
        'name = "disableExtensions",\n    build_setting_default = False,',
        'name = "disableExtensions",\n    build_setting_default = True,',
    ),
    # --- Free Apple ID: only entitlements a personal team can sign ---
    (
        "Telegram/BUILD",
        """        aps_fragment,
        app_groups_fragment,
        siri_fragment,
        associated_domains_fragment,
        icloud_fragment,
        apple_pay_merchants_fragment,
        unrestricted_voip_fragment,
        carplay_fragment,
        communication_notifications_fragment,
        notification_filtering_fragment,
        signin_fragment,
        background_gpu_fragment,
""",
        """        app_groups_fragment,
""",
    ),
    # --- App name ---
    (
        "Telegram/BUILD",
        """    <key>CFBundleDisplayName</key>
    <string>Swiftgram</string>
    <key>CFBundleIdentifier</key>
    <string>{telegram_bundle_id}</string>
    <key>CFBundleName</key>
    <string>Swiftgram</string>""",
        """    <key>CFBundleDisplayName</key>
    <string>%s</string>
    <key>CFBundleIdentifier</key>
    <string>{telegram_bundle_id}</string>
    <key>CFBundleName</key>
    <string>%s</string>""" % (APP_NAME, APP_NAME),
    ),
    # --- App Group fallback: a re-signed app may not get the group container ---
    (
        "submodules/TelegramUI/Sources/AppDelegate.swift",
        "        let maybeAppGroupUrl = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupName)\n        \n        let buildConfig",
        "        let maybeAppGroupUrl = sgAppGroupContainerURL(appGroupName)\n        \n        let buildConfig",
    ),
    (
        "submodules/TelegramUI/Sources/AppDelegate.swift",
        "        configuration.sharedContainerIdentifier = appGroupName\n",
        "        if sgHasRealAppGroupContainer(appGroupName) {\n            configuration.sharedContainerIdentifier = appGroupName\n        }\n",
    ),
    (
        "Swiftgram/SGLogging/Sources/SGLogger.swift",
        "let maybeAppGroupUrl = FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupName)",
        "let maybeAppGroupUrl = sgAppGroupContainerURL(appGroupName)",
    ),
    (
        "Swiftgram/SGLogging/BUILD",
        "    deps = [\n",
        '    deps = [\n        "//Swiftgram/SGAppGroupIdentifier:SGAppGroupIdentifier",\n',
    ),
]

# Imports that the edited files need; added only if missing.
IMPORTS = {
    "Swiftgram/SGLogging/Sources/SGLogger.swift": "import SGAppGroupIdentifier",
    "submodules/TelegramUI/Sources/AppDelegate.swift": "import SGAppGroupIdentifier",
}


def fail(message):
    print("apply_mod: ERROR: " + message)
    sys.exit(1)


def apply_edit(root, rel_path, old, new):
    path = os.path.join(root, rel_path)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    count = text.count(old)
    if count != 1:
        fail("%s: expected exactly 1 match, found %d for:\n%s" % (rel_path, count, old[:300]))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.replace(old, new))
    print("apply_mod: patched " + rel_path)


def ensure_import(root, rel_path, line):
    path = os.path.join(root, rel_path)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if line + "\n" in text:
        return
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(line + "\n" + text)
    print("apply_mod: added '%s' to %s" % (line, rel_path))


def copy_overlay(root):
    overlay = os.path.join(MOD_DIR, "overlay")
    for dirpath, _, filenames in os.walk(overlay):
        for name in filenames:
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, overlay)
            dst = os.path.join(root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            print("apply_mod: added " + rel.replace(os.sep, "/"))


def replace_icon(root):
    icon_dir = os.path.join(root, "Telegram/Telegram-iOS/Swiftgram.icon")
    if not os.path.isdir(icon_dir):
        fail("icon folder not found: " + icon_dir)
    shutil.rmtree(icon_dir)
    shutil.copytree(os.path.join(MOD_DIR, "icon/Swiftgram.icon"), icon_dir)
    print("apply_mod: replaced app icon")


def main():
    if len(sys.argv) != 2:
        fail("usage: apply_mod.py <swiftgram-checkout>")
    root = os.path.abspath(sys.argv[1])
    if not os.path.isfile(os.path.join(root, "Telegram/BUILD")):
        fail("not a Swiftgram checkout: " + root)
    copy_overlay(root)
    for rel_path, old, new in EDITS:
        apply_edit(root, rel_path, old, new)
    for rel_path, line in IMPORTS.items():
        ensure_import(root, rel_path, line)
    replace_icon(root)
    print("apply_mod: done")


if __name__ == "__main__":
    main()
