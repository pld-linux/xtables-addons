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
Version:	1.5.7
Release:	%{rel}@%{_kernel_ver_str}
License:	GPL
Group:		Networking/Daemons
Source0:	http://dev.computergmbh.de/files/xtables/%{name}-%{version}.tar.bz2
# Source0-md5:	cfd0a0997efd4084d0505f93ff28c4cf
Source1:	ipset.init
Patch0:		%{name}-libs.patch
Patch1:		%{name}-geoip-dbpath.patch
Patch2:		%{name}-help.patch
#BuildRequires:	xtables-devel >= 1.5.2
BuildRequires:	iptables-devel >= 1.4.1
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.25}
BuildRequires:	rpmbuild(macros) >= 1.379
%{?with_dist_kernel:%requires_releq_kernel}
Requires(post,postun):	/sbin/depmod
Requires:	iptables >= 1.4.1
Obsoletes:	ipset
Obsoletes:	ipset-init
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
%patch1 -p1
%patch2 -p1

%build
%configure \
	--with-kbuild=%{_kernelsrcdir} \
	--with-ksource=%{_kernelsrcdir}

export XA_TOPSRCDIR=$PWD

%if %{with kernel}
%build_kernel_modules -C extensions -m compat_xtables
%endif

%if %{with userspace}
%{__make} -C extensions
%{__make} -C extensions/ipset
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter,%{_mandir}/man8}

%if %{with kernel}
cd extensions
%install_kernel_modules -m compat_xtables -d kernel/net/netfilter
install xt_*ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/netfilter
install ipset/*.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter
cd ..
%endif

%if %{with userspace}
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/ipset

%{__make} -C extensions install \
	DESTDIR=$RPM_BUILD_ROOT
%{__make} -C extensions/ipset install \
	DESTDIR=$RPM_BUILD_ROOT

cd extensions
for m in $(cat .manpages.lst); do
	install libxt_$m.man $RPM_BUILD_ROOT%{_mandir}/man8/libxt_$m.8
done
cd ..
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}
/sbin/chkconfig --add ipset

%postun
%depmod %{_kernel_ver}
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del ipset
fi

%files
%defattr(644,root,root,755)
%if %{with userspace}
# ipset
%attr(754,root,root) /etc/rc.d/init.d/ipset
%attr(755,root,root) %{_libdir}/xtables/libipset_iphash.so
%attr(755,root,root) %{_libdir}/xtables/libipset_ipmap.so
%attr(755,root,root) %{_libdir}/xtables/libipset_ipporthash.so
%attr(755,root,root) %{_libdir}/xtables/libipset_iptree.so
%attr(755,root,root) %{_libdir}/xtables/libipset_iptreemap.so
%attr(755,root,root) %{_libdir}/xtables/libipset_macipmap.so
%attr(755,root,root) %{_libdir}/xtables/libipset_nethash.so
%attr(755,root,root) %{_libdir}/xtables/libipset_portmap.so
%attr(755,root,root) %{_sbindir}/ipset
%{_mandir}/man8/ipset.*
#
%attr(755,root,root) %{_libdir}/xtables/libxt_CHAOS.so
%attr(755,root,root) %{_libdir}/xtables/libxt_DELUDE.so
%attr(755,root,root) %{_libdir}/xtables/libxt_DHCPADDR.so
%attr(755,root,root) %{_libdir}/xtables/libxt_IPMARK.so
%attr(755,root,root) %{_libdir}/xtables/libxt_LOGMARK.so
%attr(755,root,root) %{_libdir}/xtables/libxt_SYSRQ.so
%attr(755,root,root) %{_libdir}/xtables/libxt_TARPIT.so
%attr(755,root,root) %{_libdir}/xtables/libxt_TEE.so
%attr(755,root,root) %{_libdir}/xtables/libxt_condition.so
%attr(755,root,root) %{_libdir}/xtables/libxt_dhcpaddr.so
%attr(755,root,root) %{_libdir}/xtables/libxt_fuzzy.so
%attr(755,root,root) %{_libdir}/xtables/libxt_geoip.so
%attr(755,root,root) %{_libdir}/xtables/libxt_ipp2p.so
%attr(755,root,root) %{_libdir}/xtables/libxt_portscan.so
%attr(755,root,root) %{_libdir}/xtables/libxt_quota2.so
%{_mandir}/man8/libxt_CHAOS.*
%{_mandir}/man8/libxt_DELUDE.*
%{_mandir}/man8/libxt_DHCPADDR.*
%{_mandir}/man8/libxt_IPMARK.*
%{_mandir}/man8/libxt_LOGMARK.*
%{_mandir}/man8/libxt_SYSRQ.*
%{_mandir}/man8/libxt_TARPIT.*
%{_mandir}/man8/libxt_condition.*
%{_mandir}/man8/libxt_dhcpaddr.*
%{_mandir}/man8/libxt_fuzzy.*
%{_mandir}/man8/libxt_geoip.*
%{_mandir}/man8/libxt_ipp2p.*
%{_mandir}/man8/libxt_portscan.*
%{_mandir}/man8/libxt_quota2.*
%endif
%if %{with kernel}
# ipset
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_iphash.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_ipmap.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_ipporthash.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_iptree.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_iptreemap.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_macipmap.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_nethash.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ip_set_portmap.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipt_SET.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipt_set.ko.gz
#
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/compat_xtables.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_CHAOS.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_DELUDE.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_DHCPADDR.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_IPMARK.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_LOGMARK.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_SYSRQ.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_TARPIT.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_TEE.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_condition.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_fuzzy.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_geoip.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_ipp2p.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_portscan.ko.gz
/lib/modules/%{_kernel_ver}/kernel/net/netfilter/xt_quota2.ko.gz
%endif
