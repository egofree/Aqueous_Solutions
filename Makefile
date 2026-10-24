# Local checks. See CONTRIBUTING.md, "Required checks".
.PHONY: check check-full install-hooks
check:
	scripts/check_all.sh
check-full:
	scripts/check_all.sh --full
install-hooks:
	scripts/install_pre_push_hook.sh
