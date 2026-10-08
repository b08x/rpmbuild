## START: Set by rpmautospec
## (rpmautospec version 0.8.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 1;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%global forgeurl https://github.com/ubuntu/yaru
%global tag %{version}-0ubuntu1
%global _license COPYING COPYING.LGPL-2.1 COPYING.LGPL-3.0 LICENSE_CCBYSA

Name:       yaru-theme
Version:    25.10.3
%forgemeta
Release:    %autorelease
Summary:    Ubuntu community theme "yaru"
BuildArch:  noarch

License:    GPL-3.0-or-later and CC-BY-SA-4.0
URL:        https://community.ubuntu.com/c/desktop/theme-refresh
Source0:    %{forgesource}

BuildRequires: meson >= 0.59
BuildRequires: sassc
BuildRequires: pkgconfig(appstream-glib)

Requires:   gnome-shell-theme-yaru = %{version}-%{release}
Requires:   yaru-gtk2-theme = %{version}-%{release}
Requires:   yaru-gtk3-theme = %{version}-%{release}
Requires:   yaru-gtk4-theme = %{version}-%{release}
Requires:   yaru-gtksourceview-theme = %{version}-%{release}
Requires:   yaru-icon-theme = %{version}-%{release}
Requires:   yaru-sound-theme = %{version}-%{release}

%global _description %{expand:
Yaru is the default theme for Ubuntu, backed by the community.

It contains:
  * a GNOME Shell theme based on the upstream GNOME shell theme
  * a light and dark GTK theme (gtk2 and gtk3) based on the upstream Adwaita
    Gtk theme
  * an icon & cursor theme, derived from the Unity8 Suru icons and Suru icon
    theme
  * a sound theme, combining sounds from the WoodenBeaver and Touch-Remix
    sound themes.}

%description %{_description}


%package     -n gnome-shell-theme-yaru
Summary:        Yaru GNOME Shell Theme

Requires:       gnome-shell-extension-user-theme

Recommends:     yaru-gtk3-theme
Recommends:     yaru-icon-theme

Suggests:       yaru-sound-theme
Suggests:       yaru-theme

%description -n gnome-shell-theme-yaru %{_description}

This package contains GNOME Shell Theme.


%package     -n yaru-gtk2-theme
Summary:        GTK+ 2 support for the Yaru GTK Theme

Requires:       adwaita-gtk2-theme
Requires:       gtk-murrine-engine

Recommends:     yaru-gtk3-theme

%description -n yaru-gtk2-theme %{_description}

This package contains GTK+ 2 theme.


%package     -n yaru-gtk3-theme
Summary:        GTK+ 3 support for the Yaru GTK Theme

Requires:       gtk3

Recommends:     yaru-gtk2-theme
Recommends:     yaru-gtk4-theme

%description -n yaru-gtk3-theme %{_description}

This package contains GTK+ 3 theme.


%package     -n yaru-gtk4-theme
Summary:        GTK+ 3 support for the Yaru GTK Theme

Requires:       gtk4

Recommends:     yaru-gtk2-theme
Recommends:     yaru-gtk3-theme

%description -n yaru-gtk4-theme %{_description}

This package contains GTK 4 theme.


%package     -n yaru-icon-theme
Summary:        Yaru icon theme
License:        CC-BY-SA

Requires:       hicolor-icon-theme

Suggests:       gnome-shell-theme-yaru
Suggests:       yaru-gtk3-theme
Suggests:       yaru-sound-theme

%description -n yaru-icon-theme %{_description}

This package contains the icon theme.


%package     -n yaru-sound-theme
Summary:        Yaru sound theme
License:        CC-BY-SA

%description -n yaru-sound-theme %{_description}

This package contains the sound theme following the XDG theming specification.


%package     -n yaru-gtksourceview-theme
Summary:        Yaru GtkSourceView theme
License:        CC-BY-SA

%description -n yaru-gtksourceview-theme %{_description}

This package contains the GtkSourceView theme.


%prep
%forgeautosetup -p1


%build
%meson
%meson_build


%install
%meson_install

rm  %{buildroot}%{_datadir}/glib-2.0/schemas/99_Yaru.gschema.override \
    %{buildroot}%{_datadir}/xsessions/Yaru-xorg.desktop \
    %{buildroot}%{_datadir}/wayland-sessions/Yaru.desktop \
    %{buildroot}%{_datadir}/gnome-shell/extensions/ubuntu-dock@ubuntu.com/yaru.css

touch %{buildroot}%{_datadir}/icons/Yaru/icon-theme.cache

%transfiletriggerin -- %{_datadir}/icons/Yaru
gtk-update-icon-cache --force %{_datadir}/icons/Yaru &>/dev/null || :


%files
%license %{_license}
%doc AUTHORS CONTRIBUTING.md README.md
%{_datadir}/themes/Yaru*/metacity-1/

%files -n gnome-shell-theme-yaru
%license %{_license}
%{_datadir}/gnome-shell/modes/yaru.json
%{_datadir}/gnome-shell/theme/Yaru*/
%{_datadir}/themes/Yaru-*/index.theme
%{_datadir}/themes/Yaru*/gnome-shell
%{_datadir}/themes/Yaru/index.theme

%files -n yaru-gtk2-theme
%license %{_license}
%{_datadir}/themes/Yaru-*/gtk-2.0/
%{_datadir}/themes/Yaru/gtk-2.0/
%dir %{_datadir}/themes/Yaru
%dir %{_datadir}/themes/Yaru-dark

%files -n yaru-gtk3-theme
%license %{_license}
%{_datadir}/themes/Yaru-*/gtk-3.*/
%{_datadir}/themes/Yaru/gtk-3.*/
%dir %{_datadir}/themes/Yaru
%dir %{_datadir}/themes/Yaru-dark

%files -n yaru-gtk4-theme
%license %{_license}
%{_datadir}/themes/Yaru-*/gtk-4.*/
%{_datadir}/themes/Yaru/gtk-4.*/
%dir %{_datadir}/themes/Yaru
%dir %{_datadir}/themes/Yaru-dark

%files -n yaru-icon-theme
%license %{_license}
%{_datadir}/icons/Yaru*/
%ghost %{_datadir}/icons/Yaru/icon-theme.cache

%files -n yaru-sound-theme
%license %{_license}
%{_datadir}/sounds/Yaru/

%files -n yaru-gtksourceview-theme
%license %{_license}
%{_datadir}/gtksourceview-*/styles/Yaru*.xml
%{_datadir}/libgedit-gtksourceview-300/styles/Yaru*.xml


%changelog
## START: Generated by rpmautospec
* Wed Oct 22 2025 Artem Polishchuk <ego.cordatus@gmail.com> - 25.10.3-1
- chore: Update to 25.10.3

* Fri Jul 25 2025 Fedora Release Engineering <releng@fedoraproject.org> - 25.04.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Sun Apr 27 2025 Artem Polishchuk <ego.cordatus@gmail.com> - 25.04.2-1
- chore: Update to 25.04.2

* Fri Feb 28 2025 Artem Polishchuk <ego.cordatus@gmail.com> - 24.10.4-1
- chore: Update to 24.10.4

* Sun Jan 19 2025 Fedora Release Engineering <releng@fedoraproject.org> - 24.04.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Sat Jul 20 2024 Fedora Release Engineering <releng@fedoraproject.org> - 24.04.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Fri Apr 19 2024 Artem Polishchuk <ego.cordatus@gmail.com> - 24.04.2-1
- chore: Update to 24.04.2 (rh#2276089)

* Thu Apr 18 2024 Artem Polishchuk <ego.cordatus@gmail.com> - 24.04.1-1
- chore: Update to 24.04.1 (rh#2275907)

* Fri Apr 12 2024 Artem Polishchuk <ego.cordatus@gmail.com> - 24.04.0-2
- license: Convert to SPDX

* Fri Apr 12 2024 Artem Polishchuk <ego.cordatus@gmail.com> - 24.04.0-1
- chore: Update to 24.04.0 (rh#2271153)

* Sat Jan 27 2024 Fedora Release Engineering <releng@fedoraproject.org> - 23.10.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Thu Nov 09 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.10.0-4
- build: Use 0ubuntu2 tarball

* Wed Oct 18 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.10.0-3
- build: Add Packit config

* Wed Oct 18 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.10.0-2
- build: Use forge macros

* Tue Aug 29 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.10.0-1
- chore: Update to 23.10.0 (rh#2235553)

* Sat Jul 22 2023 Fedora Release Engineering <releng@fedoraproject.org> - 23.04.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Mon May 15 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.04.4-1
- chore: Update to 23.04.4

* Wed Mar 29 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.04.2-2
- build: Drop humanity-icon-theme dep

* Tue Mar 28 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.04.2-1
- chore: Update to 23.04.2

* Sat Mar 18 2023 Artem Polishchuk <ego.cordatus@gmail.com> - 23.04.1-1
- chore: Update to 23.04.1

* Sat Jan 21 2023 Fedora Release Engineering <releng@fedoraproject.org> - 22.10.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat Sep 24 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.10.3-1
- chore(update): 22.10.3

* Sat Sep 17 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.10.2-2
- build: Update description

* Sat Sep 17 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.10.2-1
- chore(update): 22.10.2

* Thu Aug 25 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.10.1-1
- chore(update): 22.10.1

* Sat Jul 23 2022 Fedora Release Engineering <releng@fedoraproject.org> - 22.04.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Apr 25 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.04.4-2
- build: Add Requires gnome-shell-extension-user-theme

* Mon Apr 25 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.04.4-1
- chore(update): 22.04.4

* Fri Feb 25 2022 Artem Polishchuk <ego.cordatus@gmail.com> - 22.04.1-1
- chore(update): 22.04.1

* Sat Jan 22 2022 Fedora Release Engineering <releng@fedoraproject.org> - 21.10.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Sep 27 2021 Frantisek Zatloukal <fzatlouk@redhat.com> - 21.10.2-1
- build(update): 21.10.2

* Fri Jul 23 2021 Fedora Release Engineering <releng@fedoraproject.org> - 21.04.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu Apr 08 2021 Artem Polishchuk <ego.cordatus@gmail.com> - 21.04.1-2
- build: Fixes

* Tue Apr 06 2021 Artem Polishchuk <ego.cordatus@gmail.com> - 21.04.1-1
- build(update): 21.04.1

* Thu Jan 28 2021 Fedora Release Engineering <releng@fedoraproject.org> - 20.10.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Oct 11 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.10.6.1-1
- build(update): 20.10.6.1

* Tue Oct  6 19:52:37 EEST 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.10.6-1
- build(update): 20.10.6

* Thu Sep 24 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.10.4-1
- Update to 20.10.4

* Fri Sep 11 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.10.3-1
- Update to 20.10.3
- Don't build yaru-unity-theme

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20.04.6-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Apr 21 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.6-3
- Workaround for replace directory with symlink which was added in Yaru | Thanks for tip @zawertun

* Sat Apr 18 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.6-2
- Add new 'yaru-unity-theme' subpackage

* Fri Apr 17 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.6-1
- Update to 20.04.6

* Thu Apr 16 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.5-1
- Update to 20.04.5

* Tue Mar 24 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.4-1
- Update to 20.04.4

* Fri Feb 07 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 20.04.1-1
- Update to 20.04.1

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org> - 19.10.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 08 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 19.10.5-1
- Update to 19.10.5

* Thu Nov 21 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 19.10.4-1.20191118git1937b28
- Update to latest git snapshot which contain broken gnome-shell theme fix

* Fri Sep 27 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 19.10.3-1
- Update to 19.10.3
- Add new light variant
- Drop fdupes

* Tue Sep 10 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 19.10.1-2
- Update to 19.10.1

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org> - 19.04.1-3.20190425git0ddb244
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Apr 26 2019 Artem Polishchuk <ego.cordatus@gmail.com> - 19.04.1-2.20190425git0ddb244
- Adapt for Fedora

* Fri Jan 18 10:30:30 UTC 2019 - dead_mozay@opensuse.org
- Update to version 19.04+20190117.f36189f4

* Wed Jan 02 11:51:35 UTC 2019 - dead_mozay@opensuse.org
- Update to version 18.10.7+20190101.1db0abb5

## END: Generated by rpmautospec
