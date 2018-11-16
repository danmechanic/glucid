.PHONY: clean all UI

# you probably do not want to use this makefile
# nothing to see here, just to rebuild UI, and test 

all: UI

UI:
	pyrcc5 -o ./Glucid8824_rc.py ./Glucid8824.qrc
	pyuic5 --import-from=glucid -o ./Glucid8824_UI.py ./Glucid8824.ui

macbinary:
	pyinstaller -y --clean --onefile --windowed --noconsole --icon=glucid/lucid8824_icon.icns glucid/xglucid.py

winbinary:
	pyinstaller -y --clean --onefile --windowed --noconsole --icon=glucid/lucid8824_icon.ico glucid/xglucid.py

clean:
	rm ./Glucid8824_rc.py Glucid8824_UI.py

BUILD:
	(cd /home/mechanic/github/glucid; python3 setup.py sdist bdist_wheel)

INSTALL:
	pip install --upgrade /home/mechanic/github/glucid/dist/glucid-0.1.6-py3-none-any.whl
