package=gmp
$(package)_version=6.1.2
$(package)_sha256_hash=87b565e89a9a684fe4ebeeddb8399dce2599f9c9049854ca8c0dfbdea0e21912
$(package)_file_name=$(package)-$($(package)_version).tar.xz
$(package)_download_path=https://gmplib.org/download/$(package)

define $(package)_set_vars
  $(package)_config_env_x86_64_mingw32 = CC_FOR_BUILD=gcc CXX_FOR_BUILD=g++
  $(package)_config_opts=--disable-shared --enable-cxx
  $(package)_config_opts += --enable-option-checking
  $(package)_config_opts_linux=--with-pic
  $(package)_config_opts_x86_64_mingw32=--build=x86_64-linux-gnu --host=x86_64-w64-mingw32
  $(package)_config_opts_darwin += --with-pic
endef

define $(package)_preprocess_cmds
  cp -f $(BASEDIR)/config.guess $(BASEDIR)/config.sub . && \
  echo 'ac_cv_exeext=.exe' > config.cache && echo 'gmp_cv_prog_exeext_for_build=' >> config.cache
endef
define $(package)_config_cmds
  $($(package)_autoconf) --cache-file=config.cache
endef



define $(package)_build_cmds
  $(MAKE)
endef

define $(package)_stage_cmds
  $(MAKE) DESTDIR=$($(package)_staging_dir) install
endef
