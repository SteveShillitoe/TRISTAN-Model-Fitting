"""This module contains style instructions using CSS notation 
for each control/widget.  Each set of CSS instructions is saved
in a string constant. TRISTAN_GREY is the preferred style."""
TRISTAN_Green ="""
                QDialog{background-color: rgb(221, 255, 153)} 
                QPushButton {background-color: rgb(48, 153, 0);
                            text-align: centre;
                            font: bold "Arial"} 
                QPushButton:pressed {background-color: rgb(24, 77, 0);
                                    border-color: navy;}
                QComboBox {
                    background: rgb(0, 204, 0);
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;}
                QGroupBox{background-color: rgb(200, 255, 53)}
                QLabel{ font: bold "Arial" }
                """
TRISTAN_BLUE ="""
                QDialog{background-color: rgb(153, 221, 255);} 
                QPushButton {
                             background-color: rgb(0, 153, 230);
                             text-align: centre;
                             font: bold "Arial";} 
                QPushButton:pressed {background-color: rgb(0, 119, 179);}
                QComboBox {
                    background: rgb(51, 187, 255);
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    font: bold "Arial";}
                QGroupBox{background-color: rgb(102, 179, 255);
                          font: bold "Arial";  }
                QLabel{ font: bold "Arial"; }
                QDoubleSpinBox{
                        background: rgb(204, 230, 255);
                        font: bold "Arial";}
                QCheckBox{font: bold "Arial";}
                """
TRISTAN_GREY = """
                QPushButton {
                             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #CCCCCC, stop: 1 #FFFFFF);
                             border-width: 3px;
                             border-style: solid;
                             border-color: rgb(10, 10, 10);
                             border-radius: 5px;
                             text-align: centre;
                             font-weight: bold;
                             font-size: 10pt;
                             padding: 6px;} 

                QPushButton:hover {
                                   background-color: rgb(175, 175, 175);
                                   border-color: rgb(200, 51, 255);}

                QPushButton:pressed {background-color: rgb(112, 112, 112);}

                QComboBox {
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    font-size: 9pt;
                    font-weight: bold;}
                
                QComboBox:hover {
                    background-color: rgb(175, 175, 175);
                    border-color: rgb(200, 51, 255);}

                QGroupBox{
                        background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #D9D9D9, stop: 1 #FFFFFF);
                        border: 2px solid gray;
                        border-radius: 5px;
                        padding: 1em;
                        margin-top: 1em; 
                        font-weight: bold;
                        font-size: 9pt;
                          }

                


                QLabel{ padding: 4px;
                        text-align: centre;
                        font-weight: bold;
                        font-size: 8pt;
                        }

                QDoubleSpinBox{
                    padding: 4px;
                    font-size: 8pt;
                    font-weight: bold;}

                QDoubleSpinBox:hover{
                                     background-color: rgb(230, 230, 230);
                                     border-color: rgb(200, 51, 200);}

                QCheckBox{
                    font-weight: bold;
                    font-size: 9pt;}

                QCheckBox:hover{
                        background-color: rgb(175, 175, 175);
                        border-color: rgb(200, 51, 255);}

                """

