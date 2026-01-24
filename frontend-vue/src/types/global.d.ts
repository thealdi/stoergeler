export {};

declare global {
  interface Window {
    STOERGELER_BACKEND_URL?: string;
    STOERGELER_BACKEND_PATH?: string;
  }

  interface ImportMetaEnv {
    readonly VITE_APP_VERSION?: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}
