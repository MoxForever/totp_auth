from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from totp_auth.core.errors import LoaderError
from totp_auth.core.models import AuthWidget


class WidgetsLoader:
    def __init__(self, *widgets_dirs: Path):
        self._widgets_dirs = widgets_dirs
        self._widgets: dict[str, AuthWidget] = {}

        self.reload()

    def reload(self):
        self._widgets.clear()
        for widgets_dir in self._widgets_dirs:
            for widget_path in widgets_dir.glob("*.py"):
                if widget_path.stem == "__init__":
                    continue

                try:
                    self._widgets.update(
                        {w.name: w for w in self.load_widget(widget_path)}
                    )
                except Exception as e:
                    raise LoaderError(widget_path, e)

    def load_widget(self, path: Path) -> list[AuthWidget]:
        module_name = f"totp_auth.auth_widgets.{path.stem}"
        spec = spec_from_file_location(module_name, path)
        if spec is None:
            raise ValueError(f"Failed to load widget {path}")

        module = module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        widgets = [getattr(module, name)() for name in module.__all__]
        for w in widgets:
            if not isinstance(w, AuthWidget):
                raise ValueError(f"Widget {w} is not a subclass of AuthWidget")

        return widgets

    def list_widgets(self) -> list[str]:
        return list(self._widgets.keys())

    def get_widget(self, name: str) -> AuthWidget:
        return self._widgets[name]
