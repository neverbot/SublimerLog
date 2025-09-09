"""
Simple plugin reloader for Sublimer Log
Reads a list named `plugins_to_reload` from `SublimerLog.sublime-settings` and attempts
to reload matching modules/packages via `sublime_plugin.reload_plugin`.

This implementation is lightweight and avoids complex filesystem scanning. It will try
these strategies for each entry in the list (in order):

1. Treat the entry as a module name and reload modules from `sys.modules` that match
   the entry as a top-level name or start with `entry.`.
2. Attempt `sublime_plugin.reload_plugin(entry)` directly.

Entries should typically be package/module names (for example: "MyPackage" or
"my_package.module").
"""

import sys
import sublime  # type: ignore
import sublime_plugin  # type: ignore
from typing import List
import importlib
import traceback
import os
from pathlib import Path

try:
    # Prefer the plugin's logger if available
    from ..console import log
except Exception:

    def log(message: str) -> None:  # fallback
        try:
            print(message)
        except Exception:
            pass


def unload_plugin(target: str, quiet: bool = False) -> None:
    """Unload all submodules of the given plugin.

    This performs three steps:
    1. If the top-level plugin module is present, call sublime_plugin.unload_module(module)
       so Sublime's own teardown runs.
    2. Remove all matching entries from sys.modules in depth-first order (children first).
    3. Invalidate import caches.
    """
    # Step 1: tell Sublime to unload the top-level plugin module if present
    try:
        top_mod = sys.modules.get(target)
        if top_mod is not None:
            try:
                sublime_plugin.unload_module(top_mod)
                if not quiet:
                    log(f"Called sublime_plugin.unload_module on {target}")
            except Exception as e:
                log(f"sublime_plugin.unload_module failed for {target}: {e}")
    except Exception:
        # defensive - don't let unload failures stop the rest
        pass

    # Step 2: remove submodules from sys.modules (children first)
    unload_candidates = [
        name
        for name in list(sys.modules.keys())
        if name == target or name.startswith(target + ".")
    ]

    # Sort by depth (more dots first) so we delete submodules before parent
    unload_candidates.sort(key=lambda n: n.count("."), reverse=True)

    for mod_name in unload_candidates:
        try:
            # avoid trying to unload the same top-level module twice
            if mod_name in sys.modules:
                del sys.modules[mod_name]
                if not quiet:
                    log(f"Unloaded module {mod_name}")
        except Exception as e:
            log(f"Failed to unload module {mod_name}: {e}")

    # Step 3: invalidate import caches
    try:
        importlib.invalidate_caches()
    except Exception as e:
        log(f"Failed to invalidate caches: {e}")


def _gather_package_modules(package: str):
    """Return a tuple (all_modules, plugin_modules).

    - all_modules: set of module names belonging to the package (from sys.modules
      and from scanning the Packages folder).
    - plugin_modules: subset of all_modules that are top-level plugin modules
      (files directly under the package folder, e.g. Packages/PackageName/foo.py -> PackageName.foo)
    """
    all_modules = set()
    plugin_modules = set()

    # include package itself
    all_modules.add(package)

    # add modules already in sys.modules
    for name in list(sys.modules.keys()):
        if name == package or name.startswith(package + "."):
            all_modules.add(name)

    # try to scan Packages folder for .py files under the package folder
    try:
        packages_path = sublime.packages_path()
    except Exception:
        packages_path = None

    if packages_path:
        folder_path = os.path.join(packages_path, package)
        if os.path.isdir(folder_path):
            for root, _, files in os.walk(folder_path):
                for fname in files:
                    if not fname.endswith(".py"):
                        continue
                    fpath = os.path.join(root, fname)
                    rel = os.path.relpath(fpath, packages_path)
                    mod_parts = Path(rel).with_suffix("").parts
                    # Use parts exactly as found on disk; do not normalize hyphens/underscores.
                    mod_parts = list(mod_parts)
                    module_name = ".".join(mod_parts)
                    all_modules.add(module_name)
                    # plugin modules are those whose rel path is directly under package (two parts)
                    if len(mod_parts) == 2:
                        plugin_modules.add(module_name)

    # also consider the package __init__ as a plugin module
    plugin_modules.add(package)

    return all_modules, plugin_modules


def reload_plugin(target: str, quiet: bool = False) -> bool:
    """Reload a single plugin module trying to mimic Sublime Text's initial loading.

    Steps:
    1. Gather package modules and identify top-level plugin modules.
    2. Call sublime_plugin.unload_module on top-level plugin modules (if present).
    3. Remove submodules from sys.modules (depth-first) to start from clean state.
    4. Import and load modules in natural order. For top-level plugin modules use
       sublime_plugin.load_module(module) when possible; otherwise fall back to reload_plugin.
    """
    try:
        all_modules, plugin_modules = _gather_package_modules(target)
    except Exception as e:
        log(f"Failed to gather modules for {target}: {e}")
        traceback.print_exc()
        return False

    if not quiet:
        log(
            f"Found {len(all_modules)} module(s) for package '{target}', {len(plugin_modules)} top-level plugin(s)"
        )

    # Step 2: ask Sublime to unload top-level plugin modules
    for plugin in sorted(plugin_modules):
        try:
            mod = sys.modules.get(plugin)
            if mod is not None:
                try:
                    sublime_plugin.unload_module(mod)
                    if not quiet:
                        log(f"Called sublime_plugin.unload_module on {plugin}")
                except Exception as e:
                    log(
                        f"sublime_plugin.unload_module failed for {plugin}: {e}"
                    )
        except Exception:
            pass

    # Step 3: remove all package modules from sys.modules (children first)
    candidates = [
        name for name in list(sys.modules.keys()) if name in all_modules
    ]
    candidates.sort(key=lambda n: n.count("."), reverse=True)
    for name in candidates:
        try:
            if name in sys.modules:
                del sys.modules[name]
                if not quiet:
                    log(f"Unloaded module {name}")
        except Exception as e:
            log(f"Failed to remove module {name} from sys.modules: {e}")

    try:
        importlib.invalidate_caches()
    except Exception as e:
        log(f"Failed to invalidate caches: {e}")

    # Step 4: import and load modules in natural order
    modules_to_import = sorted(all_modules, key=lambda n: n.split("."))

    loaded_any = False
    for name in modules_to_import:
        try:
            if not quiet:
                log(f"Importing module: {name}")
            importlib.import_module(name)
            loaded_any = True
        except Exception as e:
            log(f"Import failed for {name}: {e}")
            traceback.print_exc()
            # continue trying others

    # Load top-level plugin modules using sublime_plugin.load_module when possible
    for plugin in sorted(plugin_modules):
        try:
            mod = sys.modules.get(plugin)
            if mod is not None:
                try:
                    if not quiet:
                        log(
                            f"Loading plugin module via sublime_plugin.load_module: {plugin}"
                        )
                    sublime_plugin.load_module(mod)
                    loaded_any = True
                except Exception:
                    if not quiet:
                        log(
                            f"sublime_plugin.load_module failed for {plugin}, falling back to reload_plugin"
                        )
                    traceback.print_exc()
                    try:
                        sublime_plugin.reload_plugin(plugin)
                        loaded_any = True
                    except Exception as e:
                        log(
                            f"sublime_plugin.reload_plugin fallback failed for {plugin}: {e}"
                        )
            else:
                # fallback: try reload_plugin by name
                try:
                    sublime_plugin.reload_plugin(plugin)
                    loaded_any = True
                except Exception as e:
                    log(
                        f"sublime_plugin.reload_plugin failed for {plugin}: {e}"
                    )
        except Exception as e:
            log(f"Error loading plugin {plugin}: {e}")

    return loaded_any


def reload_plugins(plugin_names: List[str], quiet: bool = False) -> None:
    """Reload the given list of plugin package/module names."""
    if not plugin_names:
        return

    for entry in plugin_names:
        if not entry or not isinstance(entry, str):
            if not quiet:
                log(f"Skipping invalid plugin entry: {entry!r}")
            continue

        unload_plugin(entry, quiet=quiet)
        success = reload_plugin(entry, quiet=quiet)

        if not success:
            try:
                packages_path = sublime.packages_path()
            except Exception:
                packages_path = None

            if packages_path:
                tried_files = []
                folder_name = entry
                folder_path = os.path.join(packages_path, folder_name)
                if os.path.isdir(folder_path):
                    if not quiet:
                        log(f"Found package folder: {folder_path}")
                    for root, _, files in os.walk(folder_path):
                        for fname in files:
                            if not fname.endswith(".py"):
                                continue
                            fpath = os.path.join(root, fname)
                            tried_files.append(fpath)
                            rel = os.path.relpath(fpath, packages_path)
                            mod_parts = Path(rel).with_suffix("").parts
                            # Use parts exactly as found on disk; do not normalize hyphens/underscores.
                            mod_parts = list(mod_parts)
                            module_guess = ".".join(mod_parts)
                            if not quiet:
                                log(
                                    f"Trying file {fpath} as module '{module_guess}'"
                                )
                            try:
                                try:
                                    importlib.import_module(module_guess)
                                except Exception:
                                    if not quiet:
                                        traceback.print_exc()
                                sublime_plugin.reload_plugin(module_guess)
                            except Exception as e:
                                if not quiet:
                                    log(f"Error reloading {module_guess}: {e}")

                if tried_files and not quiet:
                    log(f"Tried {len(tried_files)} files in package folder(s)")
                elif not quiet:
                    log(f"No package folder found for '{entry}'")
            elif not quiet:
                log(
                    "Could not determine Sublime Packages path to search for package files"
                )


def reload_from_settings(
    settings_name: str = "SublimerLog.sublime-settings",
    key: str = "plugins_to_reload",
) -> None:
    """Read the settings file and reload plugins listed under `key`.

    Example setting in `SublimerLog.sublime-settings`:
    {
        "plugins_to_reload": ["MyPackage", "another_package.module"]
    }
    """
    try:
        settings = sublime.load_settings(settings_name)
        entries = settings.get(key, [])
        if not isinstance(entries, list):
            log(f"'{key}' must be a list in {settings_name}")
            return
        if not entries:
            # log(
            #     f"No plugins to reload (settings key '{key}' is empty)"
            # )
            return
        reload_plugins(entries, True)
    except Exception as e:
        log(f"Failed to reload plugins from settings: {e}")
