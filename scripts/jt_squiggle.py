from PySide import QtGui, QtCore
import maya.cmds as cmds


class SquiggleUI(QtGui.QWidget):
    def __init__(self):
        super(SquiggleUI, self).__init__()
        self.enable_x = False
        self.enable_y = False
        self.origin_x = 0
        self.origin_y = 0
        self.attr_x_start = 0
        self.attr_y_start = 0
        self.current_time = 0
        self.init_ui()
        self.lazy_steps_x = []
        self.lazy_steps_y = []
        
    def init_ui(self):
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        main_layout.addStretch()

        # x input box
        x_layout = QtGui.QHBoxLayout()
        x_layout.addWidget(QtGui.QLabel("X " + u"\u21D2"))
        self.x_attr_text = QtGui.QLineEdit()
        self.x_scale_factor = QtGui.QDoubleSpinBox()
        self.x_scale_factor.setValue(.1)
        self.x_scale_factor.setMinimum(-99)
        x_layout.addWidget(self.x_attr_text)
        x_layout.addWidget(QtGui.QLabel("*"))
        x_layout.addWidget(self.x_scale_factor)

        main_layout.addLayout(x_layout)

        # y input box
        y_layout = QtGui.QHBoxLayout()
        y_layout.addWidget(QtGui.QLabel("Y " + u"\u21D2"))
        self.y_attr_text = QtGui.QLineEdit()
        self.y_scale_factor = QtGui.QDoubleSpinBox()
        self.y_scale_factor.setValue(.1)
        self.y_scale_factor.setMinimum(-99)
        y_layout.addWidget(self.y_attr_text)
        y_layout.addWidget(QtGui.QLabel("*"))
        y_layout.addWidget(self.y_scale_factor)
        main_layout.addLayout(y_layout)



        self.auto_rec_check = QtGui.QCheckBox("Auto key")
        self.auto_rec_check.setChecked(1)
        self.maintain_offset_check = QtGui.QCheckBox("Maintain Offset")
        self.maintain_offset_check.setChecked(1)
        self.key_once_check = QtGui.QCheckBox("Key once per frame")
        main_layout.addWidget(self.auto_rec_check)
        main_layout.addWidget(self.maintain_offset_check)
        main_layout.addWidget(self.key_once_check)
        main_layout.addStretch()


        self.setGeometry(300,300,300,500)
        self.setWindowTitle("Squiggle")
        self.setObjectName('jt_squiggle')

        self.x_attr_text.textChanged.connect(self.attr_strings_update)
        self.y_attr_text.textChanged.connect(self.attr_strings_update)

        # initialise text box colors
        self.attr_strings_update()


    def mouseMoveEvent(self, e):
        if self.current_time != cmds.currentTime(query=True) or not self.key_once_check.checkState():
            self.current_time = cmds.currentTime(query=True)

            for attr, enable, value, scale, origin, start, lazy_steps in [(self.x_attr_text, self.enable_x, e.x(), self.x_scale_factor, self.origin_x, self.attr_x_start, self.lazy_steps_x), 
                                                                          (self.y_attr_text, self.enable_y, e.y(), self.y_scale_factor, self.origin_y, self.attr_y_start, self.lazy_steps_y)]:
                if enable:
                    average_val = (value + lazy_steps[0] + lazy_steps[1] + lazy_steps[2] + lazy_steps[3]) / 5
                    pos = (average_val - origin) * scale.value()
                    lazy_steps = lazy_steps[1:] + [value]
                    
                    if self.maintain_offset_check.checkState():
                        cmds.setAttr(attr.text(), pos + start)
                    else:
                        cmds.setAttr(attr.text(), pos)

                    if self.auto_rec_check.checkState():
                        cmds.setKeyframe(attr.text())


    # def tabletEvent(self, e):
    #     print e.xTilt()


    def mousePressEvent(self, e):
        self.origin_x = e.x()
        self.origin_y = e.y()
        self.lazy_steps_x = [e.x()] * 5
        self.lazy_steps_y = [e.y()] * 5
        if self.enable_x:
            self.attr_x_start = cmds.getAttr(self.x_attr_text.text())
        if self.enable_y:
            self.attr_y_start = cmds.getAttr(self.y_attr_text.text())

    def attr_strings_update(self):
        self.enable_x = self.attr_string_update(self.x_attr_text)
        self.enable_y = self.attr_string_update(self.y_attr_text)


    def attr_string_update(self, attr):
        text = attr.text()
        node_attr = text.split('.')

        if text == "":
            attr.setStyleSheet("QLineEdit{background: rgb(90, 90, 90);}")
            return False
        else:
            attr.setStyleSheet("QLineEdit{background: rgb(174, 57, 57);}")

        try:
            if len(node_attr) == 2 and cmds.attributeQuery(node_attr[1], node=node_attr[0], exists=True):
                attr_type = cmds.attributeQuery(node_attr[1], node=node_attr[0], attributeType=True)
                for type_check in ['float', 'double', 'doubleLinear', 'doubleAngle']:
                    if attr_type == type_check:
                        attr.setStyleSheet("QLineEdit{background: rgb(89, 126, 84);}")
                        return True
        except:
            pass

        return False
    



