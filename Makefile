# -*- coding: us-ascii-unix -*-

NAME       = harbour-poor-maps
VERSION    = 0.26.205

DESTDIR    =
PREFIX     = /usr
DATADIR    = $(DESTDIR)$(PREFIX)/share/$(NAME)
DESKTOPDIR = $(DESTDIR)$(PREFIX)/share/applications
ICONDIR    = $(DESTDIR)$(PREFIX)/share/icons/hicolor

check:
	pyflakes geocoders guides poor routers tilesources

clean:
	rm -rf dist
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .cache */.cache */*/.cache
	rm -f rpm/*.rpm

dist:
	$(MAKE) clean
	mkdir -p dist/$(NAME)-$(VERSION)
	cp -r `cat MANIFEST` dist/$(NAME)-$(VERSION)
	tar -C dist -cJf dist/$(NAME)-$(VERSION).tar.xz $(NAME)-$(VERSION)

install:
	@echo "Installing Python files..."
	mkdir -p $(DATADIR)/poor
	cp poor/*.py $(DATADIR)/poor

	@echo "Installing QML files..."
	mkdir -p $(DATADIR)/qml
	cp qml/poor-maps.qml $(DATADIR)/qml/$(NAME).qml
	cp qml/[ABCDEFGHIJKLMNOPQRSTUVXYZ]*.qml $(DATADIR)/qml
	mkdir -p $(DATADIR)/qml/icons/navigation
	cp qml/icons/*.png $(DATADIR)/qml/icons
	cp qml/icons/navigation/*.svg $(DATADIR)/qml/icons/navigation
	mkdir -p $(DATADIR)/qml/js
	cp qml/js/*.js $(DATADIR)/qml/js

	@echo "Installing tilesources..."
	mkdir -p $(DATADIR)/tilesources
	cp tilesources/*.json $(DATADIR)/tilesources
	cp tilesources/[!_]*.py $(DATADIR)/tilesources

	@echo "Installing geocoders..."
	mkdir -p $(DATADIR)/geocoders
	cp geocoders/*.json $(DATADIR)/geocoders
	cp geocoders/[!_]*.py $(DATADIR)/geocoders
	cp geocoders/README.md $(DATADIR)/geocoders

	@echo "Installing guides..."
	mkdir -p $(DATADIR)/guides
	cp guides/*.json $(DATADIR)/guides
	cp guides/[!_]*.py $(DATADIR)/guides
	cp guides/*.qml $(DATADIR)/guides
	cp guides/README.md $(DATADIR)/guides

	@echo "Installing routers..."
	mkdir -p $(DATADIR)/routers
	cp routers/*.json $(DATADIR)/routers
	cp routers/[!_]*.py $(DATADIR)/routers
	cp routers/*.qml $(DATADIR)/routers
	cp routers/README.md $(DATADIR)/routers
	mkdir -p $(DATADIR)/routers/hsl
	cp routers/hsl/*.png $(DATADIR)/routers/hsl

	@echo "Installing desktop file..."
	mkdir -p $(DESKTOPDIR)
	cp data/$(NAME).desktop $(DESKTOPDIR)

	@echo "Installing icons..."
	mkdir -p $(ICONDIR)/86x86/apps
	mkdir -p $(ICONDIR)/108x108/apps
	mkdir -p $(ICONDIR)/128x128/apps
	mkdir -p $(ICONDIR)/256x256/apps
	cp data/poor-maps-86.png  $(ICONDIR)/86x86/apps/$(NAME).png
	cp data/poor-maps-108.png $(ICONDIR)/108x108/apps/$(NAME).png
	cp data/poor-maps-128.png $(ICONDIR)/128x128/apps/$(NAME).png
	cp data/poor-maps-256.png $(ICONDIR)/256x256/apps/$(NAME).png

rpm:
	$(MAKE) dist
	mkdir -p $$HOME/rpmbuild/SOURCES
	cp dist/$(NAME)-$(VERSION).tar.xz $$HOME/rpmbuild/SOURCES
	rm -rf $$HOME/rpmbuild/BUILD/$(NAME)-$(VERSION)
	rpmbuild -ba --nodeps rpm/$(NAME).spec
	cp $$HOME/rpmbuild/RPMS/noarch/$(NAME)-$(VERSION)-*.rpm rpm
	cp $$HOME/rpmbuild/SRPMS/$(NAME)-$(VERSION)-*.rpm rpm

test:
	py.test geocoders guides poor routers tilesources

.PHONY: check clean dist install rpm test
