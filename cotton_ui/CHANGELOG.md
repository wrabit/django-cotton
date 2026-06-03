# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

### Added

- Initial release of Django Cotton UI
- Extracted UI components from django-cotton docs as a standalone package
- A library of UI components:
  - Form controls: button, input, textarea, select, checkbox, radio, switch, combobox, field
  - Layout: card, accordion, tabs, dialog, slideover
  - Navigation: navbar, navlist, menu, dropdown
  - Feedback: badge, tooltip
  - Data: datepicker
- Tailwind CSS v4 theming via `@theme` accent tokens (Flux-style)
- Pre-built JavaScript bundle for interactive components
- CSS custom properties for easy theme customization
- Dark mode support
- `json_dumps` template filter for data serialization
