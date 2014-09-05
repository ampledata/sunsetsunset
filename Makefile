init:
	pip install -r requirements.txt

#test: init
#	python ss.py

run: init
	python ss.py
