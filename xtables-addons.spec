#
# TODO
# - kernel modules package (or not, 2 packages with mutual R?)
# - descriptions
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel
%bcond_without	userspace
#
%define		rel 0.1
Summary:	Extensible packet filtering system && extensible NAT system
Summary(pl.UTF-8):	System filtrowania pakietów oraz system translacji adresów (NAT)
Summary(pt_BR.UTF-8):	Ferramenta para controlar a filtragem de pacotes no kernel-2.6.x
Summary(ru.UTF-8):	Утилиты для управления пакетными фильтрами ядра Linux
Summary(uk.UTF-8):	Утиліти для керування пакетними фільтрами ядра Linux
Summary(zh_CN.UTF-8):	Linux内核包过滤管理工具
Name:		xtables-addons
Version:	1.5.4.1
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL
Group:		Networking/Daemons
Source0:	http://dev.computergmbh.de/files/xtables/%{name}-%{version}.tar.bz2
# Source0-md5:	f78352e9021986347cd347edc82c40c2
Patch0:		%{name}-libs.patch
#BuildRequires:	xtables-devel >= 1.5.2
BuildRequires:	iptables-devel >= 1.4.1
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.25}
BuildRequires:	rpmbuild(macros) >= 1.379
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod
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

%prep
%setup -q
%patch0 -p1

%build
%configure \
	--with-kbuild=%{_kernelsrcdir} \
	--with-ksource=%{_kernelsrcdir}
export XA_TOPSRCDIR=$PWD

%if %{with kernel}
%build_kernel_modules -C extensions -m compat_xtables
%endif

%if %{with userspace}
%{__make} -C extensions libs
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m extensions/compat_xtables -d kernel/net/netfilter
install extensions/xt_*ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/netfilter
%endif
%if %{with userspace}
%{__make} -C extensions libs_install \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%if %{with userspace}
%attr(755,root,root) %{_libdir}/xtables/libxt_CHAOS.so
%attr(755,root,root) %{_libdir}/xtables/libxt_DELUDE.so
%attr(755,root,root) %{_libdir}/xtables/libxt_IPMARK.so
%attr(755,root,root) %{_libdir}/xtables/libxt_LOGMARK.so
%attr(755,root,root) %{_libdir}/xtables/libxt_TARPIT.so
%attr(755,root,root) %{_libdir}/xtables/libxt_TEE.so
%attr(755,root,root) %{_libdir}/xtables/libxt_condition.so
%attr(755,root,root) %{_libdir}/xtables/libxt_geoip.so
%attr(755,root,root) %{_libdir}/xtables/libxt_ipp2p.so
%attr(755,root,root) %{_libdir}/xtables/libxt_portscan.so
%endif
%if %{with kernel}
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/*
%endif
