import { resolve } from "path";
import { defineConfig } from "vite";

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        enroll: resolve(__dirname, "enroll.html"),
        mpesaSubmit: resolve(__dirname, "mpesa-submit.html"),
      },
    },
  },
});
