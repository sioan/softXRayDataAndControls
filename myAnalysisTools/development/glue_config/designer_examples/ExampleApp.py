from PyQt5 import QtGui
from PyQt5 import QtWidgets
import sys
import designer_examples.design as design
import os

class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
	def __init__(self):
		# Explaining super is out of the scope of this article
		# So please google it if you're not familar with it
		# Simple reason why we use it here is that it allows us to
		# access variables, methods etc in the design.py file
		super(self.__class__, self).__init__()
		self.setupUi(self)  # This is defined in design.py file automatically
		# It sets up layout and widgets that are defined
		self.btnBrowse.clicked.connect(self.browse_folder)  # When the button is pressed
                                                            # Execute browse_folder function
		self.addThem.clicked.connect(self.goAndAddThem)

	def browse_folder(self):
		self.listWidget.clear() # In case there are any existing elements in the list
		directory = QtWidgets.QFileDialog.getExistingDirectory(self,
		                                           "Pick a folder")
		# execute getExistingDirectory dialog and set the directory variable to be equal
		# to the user selected directory

		if directory: # if user didn't pick a directory don't continue
			for file_name in os.listdir(directory): # for all files, if any, in the directory
				self.listWidget.addItem(file_name)  # add file to the listWidget

	def goAndAddThem(self):
		myResult = str(float(self.firstNumber.toPlainText())+float(self.secondNumber.toPlainText()))
		self.theResult.setText(myResult)

def main():
	app = QtWidgets.QApplication(sys.argv)
	form = ExampleApp()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
