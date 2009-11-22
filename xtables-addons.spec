#
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

%define		rel	4
Summary:	Extensible packet filtering system && extensible NAT system
Summary(pl.UTF-8):	System filtrowania pakietów oraz system translacji adresów (NAT)
Summary(pt_BR.UTF-8):	Ferramenta para controlar a filtragem de pacotes no kernel-2.6.x
Summary(ru.UTF-8):	Утилиты для управления пакетными фильтрами ядра Linux
Summary(uk.UTF-8):	Утиліти для керування пакетними фільтрами ядра Linux
Summary(zh_CN.UTF-8):	Linux内核包过滤管理工具
Name:		xtables-addons
Version:	1.18
Release:	%{rel}
License:	GPL
Group:		Networking/Admin
Source0:	http://dl.sourceforge.net/xtables-addons/%{name}-%{version}.tar.bz2
# Source0-md5:	5a8d2edbf5a3470bba58d6a60c350805
URL:		http://xtables-addons.sourceforge.net/
Patch0:		%{name}-libs.patch
Patch1:		%{name}-geoip-dbpath.patch
Patch2:		kernelrelease.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	iptables-devel >= 1.4.3
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.25}
BuildRequires:	libtool
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.379
Requires:	iptables >= 1.4.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
An extensible NAT system, and an extensible packet filtering system.
Replacement of ipchains in 2.6 and higher kernels.

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
Summary:	-
Summary(pl.UTF-8):	-
Release:	%{release}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{rel}
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-xtables-addons

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%{__sed} -i -e 's#build_ipset=m#build_ipset=n#' mconfig

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--with-kbuild=%{_kernelsrcdir} \
	--with-ksource=%{_kernelsrcdir}

export XA_TOPSRCDIR=$PWD

%if %{with kernel}
%build_kernel_modules -C extensions -m compat_xtables
%endif

%if %{with userspace}
%{__make} -C extensions
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter,%{_mandir}/man8}

%if %{with kernel}
cd extensions
%install_kernel_modules -m compat_xtables -d kernel/net/netfilter
install xt_*ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/netfilter
cd ..
%endif

%if %{with userspace}
%{__make} -C extensions install \
	DESTDIR=$RPM_BUILD_ROOT

cd extensions
for m in $(cat .manpages.lst); do
	install libxt_$m.man $RPM_BUILD_ROOT%{_mandir}/man8/libxt_$m.8
done
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-net-xtables-addons
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-xtables-addons
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/xtables/libxt_*.so
%{_mandir}/man8/libxt_*.*
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-xtables-addons
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/compat_xtables.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_*.ko.gz
%endif
