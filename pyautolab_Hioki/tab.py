from __future__ import annotations

from pyautolab_Hioki.driver import IM3536, PARAMETERS
from pyautolab_Hioki.widget import IM3536ParameterCombobox
from PySide6.QtWidgets import QCheckBox, QFormLayout, QGroupBox, QWidget

from pyautolab import api


class TabIM3536(api.DeviceTab):
    def __init__(self, device: IM3536) -> None:
        super().__init__()
        self.device = device
        self._ui = _TabUI()
        self._ui.setup_ui(self)

    def setup_settings(self) -> None:
        self._ui.combobox_parameter1.currentText()
        self.device.set_parameters(
            (
                PARAMETERS[self._ui.combobox_parameter1.currentText()],
                PARAMETERS[self._ui.combobox_parameter2.currentText()],
                PARAMETERS[self._ui.combobox_parameter3.currentText()],
                PARAMETERS[self._ui.combobox_parameter4.currentText()],
            )
        )
        self.device.set_enable_display_monitor(self._ui.checkbox_monitor_on.isChecked())
        self.device.set_enable_measure_output_auto(True)
        self.device.set_mode("LCR")
        self.device.set_speed(api.get_setting("im3536.connectingSpeed"))
        self.device.set_frequency(self._ui.slider_frequency.current_value)
        self.device.set_enable_monitor_value(self._ui.checkbox_acquire_monitor_data.isChecked())

    def get_parameters(self) -> dict[str, str]:
        self.device.set_enable_monitor_value(self._ui.checkbox_acquire_monitor_data.isChecked())
        self.device.set_parameters(
            (
                PARAMETERS[self._ui.combobox_parameter1.currentText()],
                PARAMETERS[self._ui.combobox_parameter2.currentText()],
                PARAMETERS[self._ui.combobox_parameter3.currentText()],
                PARAMETERS[self._ui.combobox_parameter4.currentText()],
            )
        )
        return self.device.get_parameters()


class _TabUI:
    def setup_ui(self, parent: QWidget) -> None:
        self.combobox_parameter1 = IM3536ParameterCombobox()
        self.combobox_parameter2 = IM3536ParameterCombobox()
        self.combobox_parameter3 = IM3536ParameterCombobox()
        self.combobox_parameter4 = IM3536ParameterCombobox()
        self.slider_frequency = api.widgets.IntSlider()
        self.checkbox_permanent = QCheckBox("Permanent Measurement")
        self.checkbox_acquire_monitor_data = QCheckBox("Acquire Voltage/Current Monitor Values")
        self.checkbox_monitor_on = QCheckBox("Monitor ON")

        # setup
        self.combobox_parameter1.setCurrentText("Rs   (Equivalent series resistance)")
        self.combobox_parameter1.set_none_disabled(True)
        self.slider_frequency.range = (4, 8_000_000)
        self.slider_frequency.update_current_value(200_000)
        self.checkbox_acquire_monitor_data.setChecked(True)
        self.checkbox_monitor_on.setChecked(True)

        # setup layout
        f_layout_parameter = QFormLayout()
        f_layout_parameter.addRow("1", self.combobox_parameter1)
        f_layout_parameter.addRow("2", self.combobox_parameter2)
        f_layout_parameter.addRow("3", self.combobox_parameter3)
        f_layout_parameter.addRow("4", self.combobox_parameter4)
        f_layout_parameter.addRow("Measurement Frequency", api.qt_helpers.add_unit(self.slider_frequency, "Hz"))

        group_option = QGroupBox("Option")
        f_layout_option = QFormLayout(group_option)
        f_layout_option.addRow(self.checkbox_acquire_monitor_data)
        f_layout_option.addRow(self.checkbox_monitor_on)

        api.qt_helpers.create_v_box_layout([f_layout_parameter, group_option], parent)
