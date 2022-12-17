#
# UPDATE WARNING: xtables-addons 3.0 support only kernels 4.15+
#                 xtables-addons 2.0 (XTADDONS_2 branch) support kernels 3.7 - 4.14
#
# Conditional build:
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)

# The goal here is to have main, userspace, package built once with
# simple release number, and only rebuild kernel packages with kernel
# version as part of release number, without the need to bump release
# with every kernel change.
%if 0%{?_pld_builder:1} && %{with kernel} && %{with userspace}
%{error:kernel and userspace cannot be built at the same time on PLD builders}
exit 1
%endif

%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	1
%define		pname	xtables-addons
Summary:	Additional extensions for xtables packet filtering system
Summary(pl.UTF-8):	Dodatkowe rozszerzenia do systemu filtrowania pakietów xtables
Name:		%{pname}%{?_pld_builder:%{?with_kernel:-kernel}}%{_alt_kernel}
Version:	3.22
Release:	%{rel}%{?_pld_builder:%{?with_kernel:@%{_kernel_ver_str}}}
License:	GPL v2
Group:		Networking/Admin
Source0:	https://inai.de/files/xtables-addons/%{pname}-%{version}.tar.xz
# Source0-md5:	cca65598ffe61a66b2da70b2c98fe923
URL:		http://xtables-addons.sourceforge.net/
BuildRequires:	autoconf >= 2.65
BuildRequires:	automake >= 1:1.11
BuildRequires:	iptables-devel >= 1.6.0
%{?with_kernel:%{expand:%buildrequires_kernel kernel%%{_alt_kernel}-module-build >= 3:4.18.0}}
BuildRequires:	libtool
BuildRequires:	pkgconfig >= 1:0.9.0
BuildRequires:	rpmbuild(macros) >= 1.746
BuildRequires:	tar >= 1.22
BuildRequires:	xz
Requires:	iptables >= 1.6.0
Obsoletes:	iptables-ipp2p
BuildRoot:	%{tmpdir}/%{pname}-%{version}-root-%(id -u -n)

%define		_duplicate_files_terminate_build	0

%description
xtables-addons is the proclaimed successor to patch-o-matic(-ng). It
contains extensions that were not accepted in the main
xtables/iptables package.

For the tools to work, you should install kernel modules, which could
be found in kernel*-net-xtables-addons.

%description -l pl.UTF-8
xtables-addons to następca patch-o-matic(-ng). Zawiera rozszerzenia,
które nie zostały zaakceptowane do głównego pakietu xtables/iptables.

Aby narzędzia działały należy zainstalować moduły jądra, które można
znaleźć w pakiecie kernel*-net-xtables-addons.

%define	kernel_pkg()\
%package -n kernel%{_alt_kernel}-net-xtables-addons\
Summary:	Kernel modules for xtables addons\
Summary(pl.UTF-8):	Moudły jądra dla rozszerzeń z pakietu xtables-addons\
Release:	%{rel}@%{_kernel_ver_str}\
Group:		Base/Kernel\
# VERSION only dependency is intentional, for allowing multiple kernel pkgs and\
# single userspace package installs.\
Requires:	%{pname} = %{version}\
Suggests:	xtables-geoip\
Conflicts:	xtables-geoip < 20090901-2\
Requires(post,postun):	/sbin/depmod\
%requires_releq_kernel\
Requires(postun):	%releq_kernel\
\
%description -n kernel%{_alt_kernel}-net-xtables-addons\
Kernel modules for xtables addons.\
\
%description -n kernel%{_alt_kernel}-net-xtables-addons -l pl.UTF-8\
Moduły jądra dla rozszerzeń z pakietu xtables-addons.\
\
%files -n kernel%{_alt_kernel}-net-xtables-addons\
%defattr(644,root,root,755)\
# restricted permissions - may contain password\
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/xt_sysrq.conf\
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/compat_xtables.ko*\
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_*.ko*\
\
%post -n kernel%{_alt_kernel}-net-xtables-addons\
%depmod %{_kernel_ver}\
\
%postun -n kernel%{_alt_kernel}-net-xtables-addons\
%depmod %{_kernel_ver}\
%{nil}

%define build_kernel_pkg()\
srcdir=${PWD:-$(pwd)}\
%build_kernel_modules XA_ABSTOPSRCDIR=$srcdir -C extensions -m compat_xtables\
for drv in extensions/compat_xtables.ko extensions/{ACCOUNT/,pknock/,}xt_*.ko ; do\
%install_kernel_modules -D installed -m ${drv%.ko} -d kernel/net/netfilter\
done\
%{nil}

%{?with_kernel:%{expand:%create_kernel_packages}}

%prep
%setup -q -n %{pname}-%{version}

%build
%configure \
	--without-kbuild

%{?with_kernel:%{expand:%build_kernel_packages}}

%if %{with userspace}
%{__make} \
	V=1
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/etc/modprobe.d

cp -a installed/* $RPM_BUILD_ROOT

cat <<'EOF' > $RPM_BUILD_ROOT/etc/modprobe.d/xt_sysrq.conf
# Set password at modprobe time. This file is secure if properly guarded,
# i.e only readable by root.
#options xt_SYSRQ password=cookies

# The hash algorithm can also be specified as a module option, for example,
# to use SHA-256 instead of the default SHA-1:
#options xt_SYSRQ hash=sha256
EOF
%endif

%if %{with userspace}
%{__make} -C extensions install \
	DESTDIR=$RPM_BUILD_ROOT
%{__make} install-man \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/libxt_ACCOUNT_cl.{la,so}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README.rst doc/{README.psd,changelog.rst}
%attr(755,root,root) %{_sbindir}/iptaccount
%attr(755,root,root) %{_sbindir}/pknlusr
%attr(755,root,root) %{_libdir}/libxt_ACCOUNT_cl.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libxt_ACCOUNT_cl.so.1
%attr(755,root,root) %{_libdir}/xtables/libxt_*.so
%{_mandir}/man8/iptaccount.8*
%{_mandir}/man8/xtables-addons.8*
%{_mandir}/man8/pknlusr.8*
%endif
