# zCLI/subsystems/zNavigation/zNavigation_modules/linking.py

from zCLI.subsystems.zParser import zExpr_eval


class Linking:
    def __init__(self, navigation):
        """Initialize linking manager."""
        self.navigation = navigation
        self.zcli = navigation.zcli
        self.logger = navigation.logger

    def handle(self, zHorizontal):
        self.walker.display.zDeclare("Handle zLink", color="ZLINK", indent=1, style="full")

        self.logger.debug("incoming zLink request: %s", zHorizontal)
        zLink_path, required_perms = self.parse_zLink_expression(zHorizontal)

        self.logger.debug("zLink_path: %s", zLink_path)
        self.logger.debug("required_perms: %s", required_perms)

        if required_perms and not self.check_zLink_permissions(required_perms):
            print("Permission denied for this section.")
            return "stop"

        zFile_parsed = self.walker.loader.handle(zLink_path)
        self.logger.debug("zFile_parsed: %s", zFile_parsed)

        selected_zBlock = zLink_path.split(".")[-1]

        path_to_file = zLink_path.rsplit(".", 1)[0]
        parts = path_to_file.split(".")
        if len(parts) >= 2:
            base_path_parts = parts[:-2]
            self.zSession["zVaFile_path"] = ".".join(base_path_parts) if base_path_parts else ""
            self.zSession["zVaFilename"] = ".".join(parts[-2:])
        else:
            self.zSession["zVaFile_path"] = ""
            self.zSession["zVaFilename"] = path_to_file
        self.zSession["zBlock"] = selected_zBlock

        active_zBlock_dict = zFile_parsed[selected_zBlock]
        zBlock_keys = list(active_zBlock_dict.keys())

        if self.walker is None:
            self.logger.error("[ERROR] No walker instance provided to ZLink.")
            return "stop"

        self.walker.zCrumbs.handle_zCrumbs(zLink_path, zBlock_keys[0])

        return self.walker.zBlock_loop(active_zBlock_dict, zBlock_keys)

    def parse_zLink_expression(self, expr):
        self.walker.display.zDeclare("zLink Parsing", color="ZLINK", indent=2, style="single")

        self.logger.info("Raw zLink expression: %s", expr)

        inner = expr[len("zLink("):-1].strip()
        self.logger.info("Stripped inner contents: %s", inner)

        if ", {" in inner:
            path_str, perms_str = inner.rsplit(", {", 1)
            zLink_path = path_str.strip()
            perms_str = "{" + perms_str.strip().rstrip("}") + "}"
            self.logger.info("Path part: %s", zLink_path)
            self.logger.info("Permissions part (raw): %s", perms_str)

            required = zExpr_eval(perms_str)
            if not isinstance(required, dict):
                self.logger.warning("strict_eval returned non-dict permissions. Defaulting to empty.")
                required = {}
            else:
                self.logger.info("Parsed required permissions: %s", required)
        else:
            zLink_path = inner
            required = {}
            self.logger.debug("[INFO] No permission block found. Path: %s", zLink_path)
        return zLink_path, required

    def check_zLink_permissions(self, required):
        self.walker.display.zDeclare("zLink Auth", color="ZLINK", indent=2, style="single")

        user = self.zSession.get("zAuth", {})
        self.logger.debug("zAuth user: %s", user)
        self.logger.debug("Required permissions: %s", required)

        if not required:
            self.logger.debug("No permissions required - allowing access.")
            return True

        for key, expected in required.items():
            actual = user.get(key)
            self.logger.debug("Checking permission key: %s | expected=%s, actual=%s", key, expected, actual)
            if actual != expected:
                self.logger.warning("Permission denied. Required %s=%s, but got %s", key, expected, actual)
                return False

        self.logger.debug("All required permissions matched.")
        return True


def handle_zLink(zHorizontal, walker=None):
    if walker is None:
        raise ValueError("handle_zLink requires a walker parameter")
        # Provide loader if missing
        from zCLI.subsystems.zLoader import zLoader
        setattr(walker, "loader", zLoader(walker))
        # Crumbs is required for navigation
        from .zCrumbs import zCrumbs
        setattr(walker, "zCrumbs", zCrumbs())
    return ZLink(walker).handle(zHorizontal)
