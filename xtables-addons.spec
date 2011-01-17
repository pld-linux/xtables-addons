# TODO
# - descriptions
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# # don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)

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

%define		rel	5
Summary:	Extensible packet filtering system && extensible NAT system
Summary(pl.UTF-8):	System filtrowania pakietów oraz system translacji adresów (NAT)
Summary(pt_BR.UTF-8):	Ferramenta para controlar a filtragem de pacotes no kernel-2.6.x
Summary(ru.UTF-8):	Утилиты для управления пакетными фильтрами ядра Linux
Summary(uk.UTF-8):	Утиліти для керування пакетними фільтрами ядра Linux
Summary(zh_CN.UTF-8):	Linux内核包过滤管理工具
Name:		xtables-addons
Version:	1.31
Release:	%{rel}
License:	GPL
Group:		Networking/Admin
Source0:	http://downloads.sourceforge.net/xtables-addons/%{name}-%{version}.tar.xz
# Source0-md5:	97ac895a67df67c28def98763023d51b
URL:		http://xtables-addons.sourceforge.net/
Patch0:		kernelrelease.patch
BuildRequires:	autoconf
BuildRequires:	automake >= 1.10.2
BuildRequires:	iptables-devel >= 1.4.3
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.25}
BuildRequires:	libtool
BuildRequires:	pkgconfig >= 0.9.0
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	tar >= 1.22
BuildRequires:	xz
Requires:	iptables >= 1.4.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# use macro, so adapter won't try to wrap
%define		kpackage	kernel%{_alt_kernel}-net-xtables-addons = %{version}-%{rel}@%{_kernel_ver_str}

%description
An extensible NAT system, and an extensible packet filtering system.
Replacement of ipchains in 2.6 and higher kernels.

You should have %{kpackage} installed for the tools to work.

%description -l pl.UTF-8
Wydajny system translacji adresów (NAT) oraz system filtrowania
pakietów. Zamiennik ipchains w jądrach 2.6 i nowszych.

%description -l pt_BR.UTF-8
Esta é a ferramenta que controla o código de filtragem de pacotes do
kernel 2.6, obsoletando ipchains. Com esta ferramenta você pode
configurar filtros de pacotes, NAT, mascaramento (masquerading),
regras dinâmicas (stateful inspection), etc.

%description -l ru.UTF-8
xtables-addons управляют кодом фильтрации сетевых пакетов в ядре
Linux. Они позволяют вам устанавливать межсетевые экраны (firewalls) и
IP маскарадинг, и т.п.

%description -l uk.UTF-8
xtables-addons управляють кодом фільтрації пакетів мережі в ядрі
Linux. Вони дозволяють вам встановлювати міжмережеві екрани
(firewalls) та IP маскарадинг, тощо.

%package -n kernel%{_alt_kernel}-net-xtables-addons
Summary:	Kernel modules for xtables addons
Summary(pl.UTF-8):	Moudły jądra dla xtables addons
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
# VERSION only dependency is intentional, for allowing multiple kernel pkgs and
# single userspace package installs.
Requires:	%{name} = %{version}
Suggests:	xtables-geoip
Conflicts:	xtables-geoip < 20090901-2
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-xtables-addons
Kernel modules for xtables addons.

%description -n kernel%{_alt_kernel}-net-xtables-addons -l pl.UTF-8
Moduły jądra dla xtables addons.

%prep
%setup -q
%patch0 -p1

%{__sed} -i -e 's#build_ipset=m#build_ipset=n#' mconfig

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-kbuild=no

%if %{with kernel}
srcdir=${PWD:-$(pwd)}
%build_kernel_modules V=1 XA_ABSTOPSRCDIR=$srcdir -C extensions -m compat_xtables
%endif

%if %{with userspace}
%{__make}
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/modprobe.d,/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter,%{_mandir}/man8}

%if %{with kernel}
cd extensions
install iptable_rawpost.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
%install_kernel_modules -m compat_xtables -d kernel/net/netfilter
install -p {ACCOUNT/,pknock/,}xt_*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/netfilter
cd ..
%endif

%if %{with userspace}
%{__make} -C extensions install \
	DESTDIR=$RPM_BUILD_ROOT

rm -f $RPM_BUILD_ROOT%{_libdir}/libxt_ACCOUNT_cl.{la,so}
# provided by iptables
rm -f $RPM_BUILD_ROOT%{_libdir}/xtables/libxt_TEE.so

cp -a xtables-addons.8 $RPM_BUILD_ROOT%{_mandir}/man8
%endif

cat <<'EOF' > $RPM_BUILD_ROOT/etc/modprobe.d/xt_sysrq.conf
# Set password at modprobe time. if this file is secure if properly guarded,
# i.e only readable by root.
#options xt_SYSRQ password=cookies

# The hash algorithm can also be specified as a module option, for example, to use SHA-256 instead of the default SHA-1:
#options xt_SYSRQ hash=sha256
EOF

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
%attr(755,root,root) %{_sbindir}/iptaccount
%attr(755,root,root) %{_libdir}/xtables/libxt_*.so
%attr(755,root,root) %{_libdir}/libxt_ACCOUNT_cl.so.*
%{_mandir}/man8/xtables-addons.8*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-xtables-addons
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) /etc/modprobe.d/xt_sysrq.conf
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/iptable_rawpost.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/compat_xtables.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_*.ko.gz
%endif
