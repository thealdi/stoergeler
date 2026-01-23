import type { GlobalThemeOverrides } from 'naive-ui';

export const themeOverrides: GlobalThemeOverrides = {
  common: {
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif',
    primaryColor: '#4a4f55',
    primaryColorHover: '#5a6067',
    primaryColorPressed: '#3f454b',
    primaryColorSuppl: '#4a4f55',
    borderRadius: '2px',
  },
  Button: {
    borderRadiusMedium: '2px',
    borderRadiusSmall: '2px',
  },
  Card: {
    borderRadius: '2px',
  },
  Pagination: {
    buttonBorderRadius: '2px',
  },
  Tag: {
    borderRadius: '2px',
  },
  DataTable: {
    borderRadius: '2px',
  },
  Menu: {
    itemTextColorActiveHorizontal: '#3b82f6',
    itemTextColorActiveHoverHorizontal: '#3b82f6',
    itemTextColorHoverHorizontal: '#3b82f6',
  },
};
