#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
#
%define		netfilter_snap		20070806
%define		llh_version		7:2.6.22.1
#
%define		rel 0.1
Summary:	Extensible packet filtering system && extensible NAT system
Summary(pl.UTF-8):	System filtrowania pakietów oraz system translacji adresów (NAT)
Summary(pt_BR.UTF-8):	Ferramenta para controlar a filtragem de pacotes no kernel-2.6.x
Summary(ru.UTF-8):	Утилиты для управления пакетными фильтрами ядра Linux
Summary(uk.UTF-8):	Утиліти для керування пакетними фільтрами ядра Linux
Summary(zh_CN.UTF-8):	Linux内核包过滤管理工具
Name:		xtables-addons
Version:	1.5.2
Release:	%{rel}
License:	GPL
Group:		Networking/Daemons
Source0:	http://dev.computergmbh.de/files/xtables/%{name}-%{version}.tar.bz2
# Source0-md5:	742ecdf7f40d5b24031cfe50f38be530
BuildRequires:	xtables-devel >= 1.5.2
%if %{with dist_kernel} && %{netfilter_snap} != 0
BuildRequires:	kernel%{_alt_kernel}-headers(netfilter) >= %{netfilter_snap}
BuildRequires:	kernel%{_alt_kernel}-source
%endif
BuildConflicts:	kernel-headers < 2.3.0
Provides:	firewall-userspace-tool
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

%build
%configure \
	--with-kbuild=%{_kernelsrcdir}/build \
	--with-ksource=%{_kernelsrcdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/xtables/*.so
%{_mandir}/man8/*
