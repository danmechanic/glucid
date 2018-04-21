.PHONY: clean all UI

all: UI

UI:
	pyrcc5 -o ./Glucid8824_rc.py ./Glucid8824.qrc
	pyuic5 --import-from=glucid -o ./Glucid8824_UI.py ./Glucid8824.ui

clean:
	rm ./Glucid8824_rc.py Glucid8824_UI.py



