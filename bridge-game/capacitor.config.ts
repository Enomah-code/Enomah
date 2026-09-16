import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.enomah.bridgearchitect",
  appName: "Architecte de Ponts",
  webDir: "dist-capacitor",
  backgroundColor: "#10151c",
  android: {
    backgroundColor: "#10151c",
  },
  ios: {
    backgroundColor: "#10151c",
    contentInset: "always",
  },
};

export default config;
