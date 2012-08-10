#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel	2
%define		pname	xtables-addons
Summary:	Additional extensions for xtables packet filtering system
Summary(pl.UTF-8):	Dodatkowe rozszerzenia do systemu filtrowania pakietów xtables
Name:		%{pname}%{_alt_kernel}
Version:	1.45
Release:	%{rel}
License:	GPL v2
Group:		Networking/Admin
Source0:	http://downloads.sourceforge.net/xtables-addons/%{pname}-%{version}.tar.xz
# Source0-md5:	802d2f556a5e545f44e4b69937bf8490
URL:		http://xtables-addons.sourceforge.net/
BuildRequires:	autoconf >= 2.65
BuildRequires:	automake >= 1:1.11
BuildRequires:	iptables-devel >= 1.4.5
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.32}
BuildRequires:	libtool
BuildRequires:	pkgconfig >= 0.9.0
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	tar >= 1.22
BuildRequires:	xz
Requires:	iptables >= 1.4.5
Obsoletes:	iptables-ipp2p
BuildRoot:	%{tmpdir}/%{pname}-%{version}-root-%(id -u -n)

# use macro, so adapter won't try to wrap
%define		kpackage	kernel%{_alt_kernel}-net-xtables-addons = %{version}-%{rel}@%{_kernel_ver_str}

%description
xtables-addons is the proclaimed successor to patch-o-matic(-ng). It
contains extensions that were not accepted in the main
xtables/iptables package.

For the tools to work, you should install kernel modules, which could
be found in %{kpackage}.

%description -l pl.UTF-8
xtables-addons to następca patch-o-matic(-ng). Zawiera rozszerzenia,
które nie zostały zaakceptowane do głównego pakietu xtables/iptables.

Aby narzędzia działały należy zainstalować moduły jądra, które można
znaleźć w pakiecie %{kpackage}.

%package -n kernel%{_alt_kernel}-net-xtables-addons
Summary:	Kernel modules for xtables addons
Summary(pl.UTF-8):	Moudły jądra dla rozszerzeń z pakietu xtables-addons
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
# VERSION only dependency is intentional, for allowing multiple kernel pkgs and
# single userspace package installs.
Requires:	%{pname} = %{version}
Suggests:	xtables-geoip
Conflicts:	xtables-geoip < 20090901-2
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-xtables-addons
Kernel modules for xtables addons.

%description -n kernel%{_alt_kernel}-net-xtables-addons -l pl.UTF-8
Moduły jądra dla rozszerzeń z pakietu xtables-addons.

%prep
%setup -q -n %{pname}-%{version}

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--without-kbuild

%if %{with kernel}
srcdir=${PWD:-$(pwd)}
%build_kernel_modules V=1 XA_ABSTOPSRCDIR=$srcdir -C extensions -m compat_xtables
%endif

%if %{with userspace}
%{__make} \
	V=1
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT{/etc/modprobe.d,/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter}
cd extensions
install iptable_rawpost.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
%install_kernel_modules -m compat_xtables -d kernel/net/netfilter
install -p {ACCOUNT/,pknock/,}xt_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/netfilter
cd ..

cat <<'EOF' > $RPM_BUILD_ROOT/etc/modprobe.d/xt_sysrq.conf
# Set password at modprobe time. This file is secure if properly guarded,
# i.e only readable by root.
#options xt_SYSRQ password=cookies

# The hash algorithm can also be specified as a module option, for example, to use SHA-256 instead of the default SHA-1:
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

%post -n kernel%{_alt_kernel}-net-xtables-addons
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-xtables-addons
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README doc/{README.psd,changelog.txt}
%attr(755,root,root) %{_sbindir}/iptaccount
%attr(755,root,root) %{_libdir}/libxt_ACCOUNT_cl.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libxt_ACCOUNT_cl.so.0
%attr(755,root,root) %{_libdir}/xtables/libxt_*.so
%{_mandir}/man8/iptaccount.8*
%{_mandir}/man8/xtables-addons.8*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-xtables-addons
%defattr(644,root,root,755)
# restricted permissions - may contain password
%attr(600,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/xt_sysrq.conf
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/iptable_rawpost.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/compat_xtables.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_*.ko.gz
%endif
