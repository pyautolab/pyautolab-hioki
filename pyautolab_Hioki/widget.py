from pyautolab_Hioki.driver import PARAMETERS

from pyautolab import api


class IM3536ParameterCombobox(api.widgets.FlexiblePopupCombobox):
    def __init__(self):
        super().__init__()
        self.addItems(PARAMETERS.keys())

    def set_none_disabled(self, is_enable: bool) -> None:
        if is_enable:
            current_text = self.currentText()
            self.clear()
            self.addItems(PARAMETERS.keys())
            self.removeItem(0)
            self.setCurrentText(current_text)
