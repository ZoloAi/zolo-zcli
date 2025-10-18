# zCLI/subsystems/zOpen/zOpen.py

"""Core zOpen handler for file and URL opening operations."""

from zCLI import os, urlparse, webbrowser, subprocess

class zOpen:
    """Core zOpen class for file and URL opening operations."""

    def __init__(self, zcli):
        """Initialize zOpen with zCLI instance."""
        if zcli is None:
            raise ValueError("zOpen requires a zCLI instance")

        if not hasattr(zcli, 'session'):
            raise ValueError("Invalid zCLI instance: missing 'session' attribute")

        self.zcli = zcli
        self.session = zcli.session
        self.logger = zcli.logger
        self.display = zcli.display
        self.zparser = zcli.zparser
        self.zfunc = zcli.zfunc
        self.dialog = zcli.dialog
        self.mycolor = "ZOPEN"

        self.display.zDeclare("zOpen Ready", color=self.mycolor, indent=0, style="full")

    def handle(self, zHorizontal):
        """Handle zOpen operations with optional hooks."""
        self.display.zDeclare("Handle zOpen", color=self.mycolor, indent=1, style="full")
        self.display.handle({"event": "zCrumbs"})  # Keep specialized event

        self.logger.debug("incoming zOpen request: %s", zHorizontal)

        # Parse input - support both string and dict formats
        if isinstance(zHorizontal, dict):
            # Dict format: {"zOpen": {"path": "...", "onSuccess": "...", "onFail": "..."}}
            zOpen_obj = zHorizontal.get("zOpen", {})
            raw_path = zOpen_obj.get("path", "")
            on_success = zOpen_obj.get("onSuccess")
            on_fail = zOpen_obj.get("onFail")
        else:
            # String format: "zOpen(path)"
            raw_path = zHorizontal[len("zOpen("):-1].strip().strip('"').strip("'")
            on_success = None
            on_fail = None

        self.logger.debug("parsed path: %s", raw_path)

        # Determine file type and route to appropriate handler
        parsed = urlparse(raw_path)

        if parsed.scheme in ("http", "https") or raw_path.startswith("www."):
            # URL handling
            url = raw_path if parsed.scheme else f"https://{raw_path}"
            result = self._open_url(url)

        elif raw_path.startswith("@") or raw_path.startswith("~"):
            # zPath handling
            result = self._open_zpath(raw_path)

        else:
            # Local file handling
            path = os.path.abspath(os.path.expanduser(raw_path))
            result = self._open_file(path)

        # Execute hooks based on result
        if result == "zBack" and on_success:
            self.logger.info("Executing onSuccess hook: %s", on_success)
            self.display.zDeclare("→ onSuccess", color=self.mycolor, indent=2, style="single")
            return self.zfunc.handle(on_success)

        if result == "stop" and on_fail:
            self.logger.info("Executing onFail hook: %s", on_fail)
            self.display.zDeclare("→ onFail", color=self.mycolor, indent=2, style="single")
            return self.zfunc.handle(on_fail)

        return result

    # ═══════════════════════════════════════════════════════════════
    # File Opening Methods
    # ═══════════════════════════════════════════════════════════════

    def _open_file(self, path):
        """Handle local file opening based on file type."""
        self.logger.debug("resolved path: %s", path)

        # Enhanced display: Show file info as JSON
        if os.path.exists(path):
            file_info = {
                "path": path,
                "exists": True,
                "size": f"{os.path.getsize(path)} bytes",
                "type": os.path.splitext(path)[1]
            }
            self.display.handle({"event": "json", "data": file_info, "color": True, "indent": 1})

        # Check if file exists
        if not os.path.exists(path):
            self.logger.error("file not found: %s", path)

            # zDialog fallback: Offer to create file or cancel
            if self.dialog:
                self.logger.info("Prompting user for action on missing file")

                try:
                    result = self.dialog.handle({
                        "zDialog": {
                            "model": None,
                            "fields": [{
                                "name": "action",
                                "type": "enum",
                                "options": ["Create file", "Cancel"]
                            }]
                        }
                    })

                    if result.get("action") == "Create file":
                        # Create empty file
                        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write("")
                        self.logger.info("Created file: %s", path)
                        self.display.zDeclare(f"Created {path}", color="GREEN", indent=1, style="single")
                        # Continue with opening the newly created file
                    else:
                        return "stop"
                except Exception as e:
                    self.logger.warning("Dialog fallback failed: %s", e)
                    return "stop"
            else:
                return "stop"

        # Route to appropriate handler based on file extension
        _, ext = os.path.splitext(path.lower())

        if ext in ['.html', '.htm']:
            return self._open_html(path)

        if ext in ['.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml']:
            return self._open_text(path)

        self.logger.warning("Unsupported file type: %s", ext)
        self.display.zDeclare(f"Unsupported file type: {ext}", color="RED", indent=1, style="single")
        return "stop"

    def _open_html(self, path):
        """Open HTML files in browser."""
        url = f"file://{path}"
        self.logger.info("opening html file: %s", url)

        try:
            success = webbrowser.open(url)
            if success:
                self.logger.info("Successfully opened HTML file in browser")
                self.display.zDeclare(
                    f"Opened {os.path.basename(path)} in browser", 
                    color="GREEN", indent=1, style="single"
                )
                return "zBack"

            self.logger.warning("Browser failed to open HTML file")
            self.display.zDeclare("Browser failed to open HTML file", color="RED", indent=1, style="single")
            return "stop"
        except Exception as e:
            self.logger.warning("Browser error: %s", e)
            self.display.zDeclare(f"Browser error: {str(e)}", color="RED", indent=1, style="single")
            return "stop"

    def _open_text(self, path):
        """Open text files using user's preferred IDE."""
        self.logger.info("opening text file: %s", path)

        # Get machine configuration
        zMachine = self.session.get("zMachine", {})
        editor = zMachine.get("ide", "nano")

        self.logger.info("Using IDE: %s", editor)

        # zDialog: Optionally ask for IDE if multiple available
        available_editors = ["cursor", "code", "nano", "vim"]
        if self.dialog and editor == "unknown":
            try:
                result = self.dialog.handle({
                    "zDialog": {
                        "model": None,
                        "fields": [{
                            "name": "ide",
                            "type": "enum",
                            "options": available_editors
                        }]
                    }
                })
                editor = result.get("ide", "nano")
            except Exception as e:
                self.logger.warning("IDE selection dialog failed: %s", e)

        # Try to open with IDE
        try:
            if os.name == 'nt':  # Windows
                try:
                    os.startfile(path)  # type: ignore
                except AttributeError:
                    subprocess.run([editor, path], check=False)
            else:  # Unix/Linux/macOS
                subprocess.run([editor, path], check=False)

            self.logger.info("Successfully opened file with %s", editor)
            self.display.zDeclare(
                f"Opened {os.path.basename(path)} in {editor}",
                color="GREEN", indent=1, style="single"
            )
            return "zBack"

        except Exception as e:
            self.logger.warning("Failed to open with IDE %s: %s", editor, e)
            self.display.zDeclare(f"Failed to open with {editor}: {str(e)}", color="RED", indent=1, style="single")

            # Fallback: Display file content
            return self._display_file_content(path)

    def _display_file_content(self, path):
        """Display text file content when IDE opening fails."""
        self.logger.info("Displaying text file content")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.display.zDeclare(f"File Content: {os.path.basename(path)}", color="INFO", indent=1, style="~")

            # Display content using display.block()
            if len(content) > 1000:
                self.display.block(content[:1000] + "...")
                self.display.line(f"\n[Content truncated - showing first 1000 of {len(content)} characters]")
            else:
                self.display.block(content)

            return "zBack"

        except Exception as e:
            self.logger.error("Failed to read file: %s", e)
            return "stop"

    # ═══════════════════════════════════════════════════════════════
    # URL Opening Methods
    # ═══════════════════════════════════════════════════════════════

    def _open_url(self, url):
        """Handle URL opening using user's preferred browser."""
        self.logger.info("opening url: %s", url)

        # Enhanced display: Show URL info as JSON
        parsed = urlparse(url)
        url_info = {
            "url": url,
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path
        }
        self.display.handle({"event": "json", "data": url_info, "color": True, "indent": 1})

        # Get machine configuration
        zMachine = self.session.get("zMachine", {})
        browser = zMachine.get("browser")

        if browser:
            self.logger.info("Using browser: %s", browser)

        # Try to open with user's preferred browser or default
        return self._open_url_browser(url, browser)

    def _open_url_browser(self, url, browser):
        """Open URL in specified or default browser."""
        try:
            if browser and browser not in ("unknown", "Safari", "Edge"):
                # Try to use specific browser if available
                from zCLI import shutil
                if shutil.which(browser):
                    subprocess.run([browser, url], check=False)
                    self.logger.info("Successfully opened URL in %s", browser)
                    self.display.zDeclare(f"Opened URL in {browser}", color="GREEN", indent=1, style="single")
                    return "zBack"

            # Fallback to system default browser (webbrowser module)
            success = webbrowser.open(url)
            if success:
                self.logger.info("Successfully opened URL in system default browser")
                self.display.zDeclare("Opened URL in default browser", color="GREEN", indent=1, style="single")
                return "zBack"
            else:
                self.logger.warning("Browser failed to open URL")
                self.display.zDeclare("Browser failed to open URL", color="RED", indent=1, style="single")
                return self._display_url_fallback(url)

        except Exception as e:
            self.logger.warning("Browser error: %s", e)
            self.display.zDeclare(f"Browser error: {str(e)}", color="RED", indent=1, style="single")
            return self._display_url_fallback(url)

    def _display_url_fallback(self, url):
        """Display URL information when opening fails."""
        self.logger.warning("Unable to open URL. Displaying information instead.")

        self.display.zDeclare("URL Information", color="INFO", indent=1, style="~")
        self.display.line(f"URL: {url}")
        self.display.line("Unable to open in browser. Please copy and paste into your browser.")
        return "zBack"

    # ═══════════════════════════════════════════════════════════════
    # zPath Resolution Methods
    # ═══════════════════════════════════════════════════════════════

    def _open_zpath(self, zPath):
        """Handle zPath opening (workspace-relative and absolute paths)."""
        self.logger.debug("resolving zPath: %s", zPath)

        # Resolve zPath to absolute filesystem path
        path = self._resolve_zpath(zPath)

        if not path:
            self.logger.error("Failed to resolve zPath: %s", zPath)
            self.display.zDeclare(f"Failed to resolve zPath: {zPath}", color="RED", indent=1, style="single")
            return "stop"

        # Open the resolved file
        return self._open_file(path)

    def _resolve_zpath(self, zPath):
        """Translate a zPath to an absolute filesystem path."""
        # Clean the zPath
        zPath = zPath.lstrip(".")
        parts = zPath.split(".")

        if parts[0] == "@":
            # Workspace-relative path
            base = self.session.get("zWorkspace") or ""
            if not base:
                self.logger.error("No workspace set for relative path: %s", zPath)
                return None
            parts = parts[1:]
        elif parts[0] == "~":
            # Absolute path
            base = os.path.sep
            parts = parts[1:]
        else:
            # Treat as normal filesystem path
            base = ""

        if len(parts) < 2:
            self.logger.error("invalid zPath: %s", zPath)
            return None

        # Reconstruct file path
        *dirs, filename, ext = parts
        file_name = f"{filename}.{ext}"

        try:
            resolved_path = os.path.abspath(os.path.join(base, *dirs, file_name))
            self.logger.debug("resolved zPath '%s' to: %s", zPath, resolved_path)
            return resolved_path
        except Exception as e:
            self.logger.error("Failed to resolve zPath '%s': %s", zPath, e)
            return None


# Export main component
__all__ = ["zOpen"]
