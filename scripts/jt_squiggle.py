from PySide import QtGui, QtCore
import maya.cmds as cmds

class SquiggleGrid(QtGui.QWidget):
    def __init__(self):
        super(SquiggleGrid, self).__init__()
        self.key_once = False
        self.absolute = False
        self.x_attr = ''
        self.y_attr = ''
        self.x_scale_factor = 1
        self.y_scale_factor = 1
        self.reset_origin()
        self.enable_x = True
        self.enable_y = True
        self.origin_x = 0
        self.origin_y = 0
        self.x_attr_start = 0
        self.y_attr_start = 0
        self.current_time = 0
        self.lazy_steps_x = []
        self.lazy_steps_y = []
        self.autokey = True


    def resizeEvent(self, e):
        self.reset_origin()

    def paintEvent(self, e):
        # update size
        contents = self.contentsRect()
        self.width = contents.width()
        self.height = contents.height()

        # paint
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        # backdrop
        qp.setPen(QtCore.Qt.NoPen)
        qp.setBrush(QtGui.QColor("#333"))
        qp.drawRect(0,0, self.width, self.height)

        # grid
        for step_size, color in [(1, QtGui.QColor("#444")), (10, QtGui.QColor("#666"))]:
            qp.setPen(color)
            for scale_factor, axis_length, axis, origin in [(self.x_scale_factor, self.width, 'x', self.origin_x),
                                                            (self.y_scale_factor, self.height, 'y', self.origin_y)]:
                if scale_factor != 0:
                    scale = scale_factor
                    if scale_factor < 0:
                        scale *= -1
                    step = step_size / scale
                    if step > 3:
                        i = 0
                        if axis == 'x':
                            while i < axis_length:
                                i += step
                                qp.drawLine(origin + i,  0, origin + i, self.height)
                                qp.drawLine(origin - i,  0, origin - i, self.height)
                        else:
                            while i < axis_length:
                                i += step
                                qp.setPen(color)    
                                qp.drawLine(0, origin + i, self.width, origin + i)
                                qp.drawLine(0, origin - i, self.width, origin - i) 


        # cross hair
        qp.setPen(QtGui.QColor("#999"))
        qp.drawLine(self.origin_x,  0, self.origin_x, self.height)
        qp.drawLine(0, self.origin_y, self.width, self.origin_y)

    def set_scale(self, x, y):
        self.x_scale_factor = x
        self.y_scale_factor = y
        self.update()

    def reset_origin(self):
        self.origin_x = self.contentsRect().width() / 2
        self.origin_y = self.contentsRect().height() / 2
        self.update()

    def mousePressEvent(self, e):
        self.origin_x = e.x()
        self.origin_y = e.y()
        if self.enable_x:
            self.x_attr_start = cmds.getAttr(self.x_attr)
        if self.enable_y:
            self.y_attr_start = cmds.getAttr(self.y_attr)

        self.lazy_steps_x = [e.x()] * 4
        self.lazy_steps_y = [e.y()] * 4
        self.update()

    def mouseReleaseEvent(self, e):
        self.reset_origin()

    def mouseMoveEvent(self, e):
        if self.current_time != cmds.currentTime(query=True) or not self.key_once:
            self.current_time = cmds.currentTime(query=True)
            
            for attr, enable, value, scale, origin, start, lazy_steps in [(self.x_attr, self.enable_x, e.x(), self.x_scale_factor, self.origin_x, self.x_attr_start, self.lazy_steps_x), 
                                                                          (self.y_attr, self.enable_y, e.y(), self.y_scale_factor, self.origin_y, self.y_attr_start, self.lazy_steps_y)]:
                if enable:
                    average_val = (value + lazy_steps[0] + lazy_steps[1] + lazy_steps[2] + lazy_steps[3]) / 5
                    pos = (average_val - origin) * scale
                    lazy_steps = lazy_steps[1:] + [value]
                    
                    if not self.absolute:
                        cmds.setAttr(attr, pos + start)
                    else:

                        cmds.setAttr(attr, pos)

                    if self.autokey:
                        cmds.setKeyframe(attr)


class SquiggleUI(QtGui.QWidget):
    def __init__(self):
        super(SquiggleUI, self).__init__()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QtGui.QVBoxLayout()
        self.setLayout(main_layout)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        self.grid = SquiggleGrid()
        main_layout.addWidget(self.grid)

        # x input box
        x_layout = QtGui.QHBoxLayout()
        x_layout.addWidget(QtGui.QLabel("X " + u"\u21D2"))
        self.x_attr_text = QtGui.QLineEdit()
        self.x_scale_factor_spin_box = QtGui.QDoubleSpinBox()
        self.x_scale_factor_spin_box.setValue(.1)
        self.x_scale_factor_spin_box.setMinimum(-99)
        self.x_scale_factor_spin_box.setSingleStep(0.1)
        x_layout.addWidget(self.x_attr_text)
        x_layout.addWidget(QtGui.QLabel("*"))
        x_layout.addWidget(self.x_scale_factor_spin_box)

        main_layout.addLayout(x_layout)

        # y input box
        y_layout = QtGui.QHBoxLayout()
        y_layout.addWidget(QtGui.QLabel("Y " + u"\u21D2"))
        self.y_attr_text = QtGui.QLineEdit()
        self.y_scale_factor_spin_box = QtGui.QDoubleSpinBox()
        self.y_scale_factor_spin_box.setValue(.1)
        self.y_scale_factor_spin_box.setMinimum(-99)
        self.y_scale_factor_spin_box.setSingleStep(0.1)
        y_layout.addWidget(self.y_attr_text)
        y_layout.addWidget(QtGui.QLabel("*"))
        y_layout.addWidget(self.y_scale_factor_spin_box)
        main_layout.addLayout(y_layout)


        self.autokey_check = QtGui.QCheckBox("Auto key")
        self.autokey_check.setChecked(1)
        self.absolute_check = QtGui.QCheckBox("Absolute positions")
        self.absolute_check.setChecked(0)
        self.key_once_check = QtGui.QCheckBox("Key once per frame")
        main_layout.addWidget(self.autokey_check)
        main_layout.addWidget(self.absolute_check)
        main_layout.addWidget(self.key_once_check)


        self.setGeometry(300,300,300,500)
        self.setWindowTitle("Squiggle")
        self.setObjectName('jt_squiggle')

        self.x_attr_text.textChanged.connect(self.attr_strings_update)
        self.y_attr_text.textChanged.connect(self.attr_strings_update)
        self.x_scale_factor_spin_box.valueChanged.connect(self.update_scale_factors)
        self.y_scale_factor_spin_box.valueChanged.connect(self.update_scale_factors)
        self.key_once_check.stateChanged.connect(self.update_key_once)
        self.absolute_check.stateChanged.connect(self.update_absolute)
        self.autokey_check.stateChanged.connect(self.update_autokey)

        self.attr_strings_update()
        self.update_scale_factors()


    def update_scale_factors(self):
        self.grid.set_scale(self.x_scale_factor_spin_box.value(), self.y_scale_factor_spin_box.value())

    def update_key_once(self):
        self.grid.key_once = self.key_once_check.checkState()

    def update_absolute(self):
        self.grid.absolute = self.absolute_check.checkState()

    def update_autokey(self):
        self.grid.autokey = self.autokey_check.checkState()

    def attr_strings_update(self):
        self.grid.enable_x = self.attr_string_update(self.x_attr_text)
        if self.grid.enable_x:
            self.grid.x_attr = self.x_attr_text.text()
        self.grid.enable_y = self.attr_string_update(self.y_attr_text)
        if self.grid.enable_y:
            self.grid.y_attr = self.y_attr_text.text()

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
    



