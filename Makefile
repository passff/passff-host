
VERSION ?= testing
BROWSER ?= firefox

SRC_DIR := ./src
TARGET_DIR := ./bin/$(VERSION)

INSTALL_WIN_FILE := install_host_app.bat
INSTALL_WIN_SRC := $(SRC_DIR)/$(INSTALL_WIN_FILE)
INSTALL_WIN_TARGET := $(TARGET_DIR)/$(INSTALL_WIN_FILE)

INSTALL_UNIX_FILE := install_host_app.sh
INSTALL_UNIX_SRC := $(SRC_DIR)/$(INSTALL_UNIX_FILE)
INSTALL_UNIX_TARGET := $(TARGET_DIR)/$(INSTALL_UNIX_FILE)

HOST_APP_FILES := passff.py passff.json
HOST_APP_SRC := $(addprefix $(SRC_DIR)/,$(HOST_APP_FILES))
HOST_APP_TARGET := $(addprefix $(TARGET_DIR)/,$(HOST_APP_FILES))

HOST_TARGETS := $(INSTALL_WIN_TARGET) $(INSTALL_UNIX_TARGET) $(HOST_APP_TARGET)

all: $(HOST_TARGETS)

install: install-unix
install-unix: $(HOST_TARGETS)
	$(INSTALL_UNIX_TARGET) --local $(BROWSER)
install-win: $(HOST_TARGETS)
	$(INSTALL_WIN_TARGET) --local $(BROWSER)

%/.d:
	mkdir -p $(@D)
	@touch $@

$(HOST_TARGETS): $(TARGET_DIR)/%: $(SRC_DIR)/% $(TARGET_DIR)/.d
	sed -e "s/_VERSIONHOLDER_/$(VERSION)/g" < $(SRC_DIR)/$* > $@
	# Make scripts executable
	echo $@ | grep -vq '\(\.sh\|\.py\)$$' || chmod a+x $@

clean:
	rm -rf $(TARGET_DIR)

.PRECIOUS: %/.d
