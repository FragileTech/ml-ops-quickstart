# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
NOTEBOOKS_SRC_DIR  = ../notebooks
NOTEBOOKS_BUILD_DIR  = ./source/notebooks


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: server
server:
	python3 -m http.server --directory  build/html/

#	rm -rf source/notebooks
#	cp -r ../notebooks ./source/notebooks

.PHONY: test
test:
	if [ -e "${NOTEBOOKS_SRC_DIR}" ] && [ -e "${NOTEBOOKS_BUILD_DIR}" ]; then \
		echo "${NOTEBOOKS_BUILD_DIR} Updating notebook folder."; \
		rm -rf "${NOTEBOOKS_BUILD_DIR}"; \
		cp -r "${NOTEBOOKS_SRC_DIR}"  "${NOTEBOOKS_BUILD_DIR}"; \
	fi
	make html
	make server