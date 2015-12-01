Name: libbsoncompare		
Version: 1.2.1
Release: 8%{?dist}.db
Summary: compares bson docs	

Group:	bauman	
License: MIT	
URL:	TBD	
Source0: bsoncompare.c
Source1: mongoc-matcher.c
Source2: mongoc-matcher-op.c
Source3: mongoc-error.h
Source4: mongoc-matcher.h
Source5: mongoc-matcher-op-private.h
Source6: mongoc-matcher-private.h
Source7: bsoncompare.h
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: gcc, libbson-devel == %{version}, libbson == %{version}, pcre-devel, uthash-devel
Requires: libbson == %{version}, pcre

%description
Provides a shared object which can be used to perform mongo-like queries against BSON data.

%package devel
Summary: Development files for libbsoncompare
Requires: libbsoncompare == %{version}
Group: Development/Libraries


%description devel
The %{Name}-devel package contains libraries and header files for
developing applications that use %{Name}.


%prep
cp -fp %{SOURCE3} ./
cp -fp %{SOURCE4} ./
cp -fp %{SOURCE5} ./
cp -fp %{SOURCE6} ./
cp -fp %{SOURCE7} ./
#%setup -q

%build
#rm -rf %{buildroot}
mkdir -p %{buildroot}
gcc -I/usr/include/libbson-1.0 -lbson-1.0 -lpcre -shared -o $RPM_BUILD_DIR/libbsoncompare.so -fPIC %{SOURCE0} %{SOURCE1} %{SOURCE2}

%install
mkdir -p $RPM_BUILD_ROOT/%{_usr}/%{_lib}
install -m 644 -p $RPM_BUILD_DIR/libbsoncompare.so $RPM_BUILD_ROOT/%{_usr}/%{_lib}/libbsoncompare.so

mkdir -p $RPM_BUILD_ROOT/%{_includedir}
install -m 644 -p $RPM_BUILD_DIR/bsoncompare.h $RPM_BUILD_ROOT/%{_includedir}/bsoncompare.h
install -m 644 -p $RPM_BUILD_DIR/mongoc-error.h $RPM_BUILD_ROOT/%{_includedir}/mongoc-error.h
install -m 644 -p $RPM_BUILD_DIR/mongoc-matcher.h $RPM_BUILD_ROOT/%{_includedir}/mongoc-matcher.h
install -m 644 -p $RPM_BUILD_DIR/mongoc-matcher-op-private.h $RPM_BUILD_ROOT/%{_includedir}/mongoc-matcher-op-private.h
install -m 644 -p $RPM_BUILD_DIR/mongoc-matcher-private.h $RPM_BUILD_ROOT/%{_includedir}/mongoc-matcher-private.h


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{_usr}/%{_lib}/libbsoncompare.so
%doc

%files devel
%{_includedir}/*.h


%changelog
