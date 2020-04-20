publish-test:
	rm -r dist/*
	python setup.py sdist
	twine upload -r pypitest dist/*

publish:
	#rm -r dist
	python3 setup.py sdist bdist_wheel
	twine check dist/*
	twine upload dist/*