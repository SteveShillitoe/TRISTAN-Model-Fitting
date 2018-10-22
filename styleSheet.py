"""This module contains style instructions using CSS notation for each control/widget """
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
Blue_Scheme ="""
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
GREY_SCALE = """
                QPushButton {
                             background-color: rgb(191, 191, 191);
                             border-width: 2px;
                             border-style: solid;
                             border-color: rgb(10, 10, 10);
                             border-radius: 5px;
                             text-align: centre;
                             font: bold "Arial";} 
                QPushButton:hover {background-color: rgb(150, 150, 150);
                                   border-color: rgb(200, 51, 255);
                                   }
                QPushButton:pressed {background-color: rgb(112, 112, 112);}
                QComboBox {
                    border: 1px solid gray;
                    border-radius: 3px;
                    padding: 1px 18px 1px 3px;
                    min-width: 6em;
                    font: bold "Arial";}
                
                QComboBox:hover {
                    background-color: rgb(150, 150, 150);
                    border-color: rgb(200, 51, 255);}

                QGroupBox{
                        background-color: rgb(217, 217, 217); 
                        border: 1px solid gray;
                        border-radius: 5px;
                        padding: 1em;
                        margin-top: 1em; 
                        font: bold "Arial";  }
                QLabel{ font: bold "Arial"; }
                QDoubleSpinBox{
                        font: bold "Arial";}
                QCheckBox{font: bold "Arial";}
                """

